from flask import Blueprint, flash, redirect, render_template, request, jsonify, session, url_for
from wakeonlan import send_magic_packet
from app.models import Equipo, User, db
from app.utils import obtenerPorMac, ping
from app.auth_middleware import token_required, admin_required, can_access_equipo

main = Blueprint('main', __name__)

# ============================================================================
# RUTAS WEB EXISTENTES (mantenidas para compatibilidad)
# ============================================================================

@main.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    equipos = Equipo.query.all()
    resultados = []
    for equipo in equipos:
        direccion_ip = obtenerPorMac(equipo.mac_address)
        if direccion_ip:
            estado = "Encendido" if ping(direccion_ip) else "Apagado"
            resultados.append({
                'id': equipo.id,
                'nombre': equipo.nombre,
                'mac_address': equipo.mac_address,
                'ip_address': direccion_ip,
                'estado': estado
            })
        else:
            resultados.append({
                'id': equipo.id,
                'nombre': equipo.nombre,
                'mac_address': equipo.mac_address,
                'ip_address': "No disponible",
                'estado': "Desconocido"
            })
    return render_template('index.html', resultados=resultados)

@main.route('/encender/<int:id>')
def encender_equipo(id):
    equipo = Equipo.query.get(id)
    if equipo:
        flash("Equipo encendido: {} (MAC: {})".format(equipo.nombre, equipo.mac_address), 'success')
        send_magic_packet(equipo.mac_address)
        return redirect(url_for('main.home'))
    else:
        return "Equipo no encontrado"

# ============================================================================
# ENDPOINTS API CON CONTROL DE ROLES
# ============================================================================

@main.route('/equipos', methods=['GET'])
@token_required
def get_equipos(current_user):
    """Obtiene equipos según permisos del usuario"""
    try:
        if current_user.is_admin():
            # Admin ve todos los equipos
            equipos = Equipo.query.all()
        else:
            # Usuario normal solo ve equipos asignados
            equipos = current_user.get_equipos_permitidos()
        
        # Enriquecer con información de estado
        resultados = []
        for equipo in equipos:
            direccion_ip = obtenerPorMac(equipo.mac_address)
            estado = "desconocido"
            
            if direccion_ip:
                estado = "encendido" if ping(direccion_ip) else "apagado"
                equipo.ip_address = direccion_ip
                equipo.estado = estado
            
            resultados.append(equipo.serialize())
        
        return jsonify({
            'success': True,
            'equipos': resultados,
            'total': len(resultados),
            'user_role': current_user.role
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/equipos/<int:equipo_id>', methods=['GET'])
@token_required
@can_access_equipo
def get_equipo(current_user, equipo_id):
    """Obtiene un equipo específico"""
    try:
        equipo = Equipo.query.get_or_404(equipo_id)
        include_users = current_user.is_admin()
        
        # Actualizar estado en tiempo real
        direccion_ip = obtenerPorMac(equipo.mac_address)
        if direccion_ip:
            equipo.ip_address = direccion_ip
            equipo.estado = "encendido" if ping(direccion_ip) else "apagado"
        
        return jsonify({
            'success': True,
            'equipo': equipo.serialize(include_users=include_users)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/equipos', methods=['POST'])
@token_required
@admin_required
def create_equipo(current_user):
    """Crear nuevo equipo (solo admin)"""
    try:
        data = request.get_json()
        
        # Verificar campos requeridos
        if not data.get('nombre') or not data.get('mac_address'):
            return jsonify({
                'success': False, 
                'message': 'Nombre y MAC address son requeridos'
            }), 400
        
        # Crear equipo
        nuevo_equipo = Equipo(
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            mac_address=data['mac_address'].upper(),
            ip_address=data.get('ip_address'),
            estado=data.get('estado', 'desconocido')
        )
        
        db.session.add(nuevo_equipo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Equipo creado exitosamente',
            'equipo': nuevo_equipo.serialize()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/equipos/<int:equipo_id>', methods=['PUT'])
@token_required
@admin_required
def update_equipo(current_user, equipo_id):
    """Actualizar equipo (solo admin)"""
    try:
        equipo = Equipo.query.get_or_404(equipo_id)
        data = request.get_json()
        
        # Actualizar campos
        if 'nombre' in data:
            equipo.nombre = data['nombre']
        if 'descripcion' in data:
            equipo.descripcion = data['descripcion']
        if 'mac_address' in data:
            equipo.mac_address = data['mac_address'].upper()
        if 'ip_address' in data:
            equipo.ip_address = data['ip_address']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Equipo actualizado exitosamente',
            'equipo': equipo.serialize()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/equipos/<int:equipo_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_equipo(current_user, equipo_id):
    """Eliminar equipo (solo admin)"""
    try:
        equipo = Equipo.query.get_or_404(equipo_id)
        nombre = equipo.nombre
        
        db.session.delete(equipo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Equipo {nombre} eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/equipos/<int:equipo_id>/encender', methods=['POST'])
@token_required
@can_access_equipo
def wake_equipo(current_user, equipo_id):
    """Encender equipo (solo si tiene acceso)"""
    try:
        equipo = Equipo.query.get_or_404(equipo_id)
        
        # Enviar paquete Wake-on-LAN
        send_magic_packet(equipo.mac_address)
        
        # Log de la acción
        print(f"Usuario {current_user.username} encendió equipo {equipo.nombre}")
        
        return jsonify({
            'success': True,
            'message': f'Comando de encendido enviado a {equipo.nombre}',
            'equipo_id': equipo_id,
            'user': current_user.username
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/equipos/<int:equipo_id>/estado', methods=['GET'])
@token_required
@can_access_equipo
def get_equipo_status(current_user, equipo_id):
    """Obtener estado actual de un equipo"""
    try:
        equipo = Equipo.query.get_or_404(equipo_id)
        
        # Verificar estado en tiempo real
        direccion_ip = obtenerPorMac(equipo.mac_address)
        if direccion_ip:
            estado = "encendido" if ping(direccion_ip) else "apagado"
            equipo.ip_address = direccion_ip
            equipo.estado = estado
            db.session.commit()
        
        return jsonify({
            'success': True,
            'equipo': equipo.serialize()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================================================
# ENDPOINTS DE ADMINISTRACIÓN (solo admin)
# ============================================================================

@main.route('/admin/users', methods=['GET'])
@token_required
@admin_required
def get_all_users(current_user):
    """Obtiene todos los usuarios (solo admin)"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'users': [user.serialize() for user in users],
            'total': len(users)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/admin/users', methods=['POST'])
@token_required
@admin_required
def create_user(current_user):
    """Crear nuevo usuario (solo admin)"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Username y password son requeridos'
            }), 400
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'message': 'El usuario ya existe'
            }), 400
        
        # Crear usuario
        nuevo_user = User(
            username=data['username'],
            password=data['password'],  # En producción: hash the password
            role=data.get('role', 'user')
        )
        
        db.session.add(nuevo_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuario creado exitosamente',
            'user': nuevo_user.serialize()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/admin/assign-equipo', methods=['POST'])
@token_required
@admin_required
def assign_equipo_to_user(current_user):
    """Asignar equipo a usuario (solo admin)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        equipo_id = data.get('equipo_id')
        
        if not user_id or not equipo_id:
            return jsonify({
                'success': False,
                'message': 'user_id y equipo_id son requeridos'
            }), 400
        
        user = User.query.get_or_404(user_id)
        equipo = Equipo.query.get_or_404(equipo_id)
        
        # Verificar si ya está asignado
        if equipo in user.equipos_asignados:
            return jsonify({
                'success': False,
                'message': f'El equipo {equipo.nombre} ya está asignado a {user.username}'
            }), 400
        
        # Asignar equipo
        user.equipos_asignados.append(equipo)
        
        # Asignación básica (metadatos simplificados)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Equipo {equipo.nombre} asignado a {user.username}',
            'user_id': user_id,
            'equipo_id': equipo_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/admin/unassign-equipo', methods=['POST'])
@token_required
@admin_required
def unassign_equipo_from_user(current_user):
    """Desasignar equipo de usuario (solo admin)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        equipo_id = data.get('equipo_id')
        
        user = User.query.get_or_404(user_id)
        equipo = Equipo.query.get_or_404(equipo_id)
        
        if equipo not in user.equipos_asignados:
            return jsonify({
                'success': False,
                'message': f'El equipo {equipo.nombre} no está asignado a {user.username}'
            }), 400
        
        # Desasignar equipo
        user.equipos_asignados.remove(equipo)
        
        # Desasignación automática con la relación
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Equipo {equipo.nombre} desasignado de {user.username}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================================================
# ENDPOINTS DE INFORMACIÓN DEL USUARIO
# ============================================================================

@main.route('/me', methods=['GET'])
@token_required
def get_current_user_info(current_user):
    """Obtiene información del usuario actual"""
    try:
        equipos = current_user.get_equipos_permitidos()
        
        return jsonify({
            'success': True,
            'user': current_user.serialize(),
            'equipos_count': len(equipos),
            'permissions': {
                'is_admin': current_user.is_admin(),
                'can_create_equipos': current_user.is_admin(),
                'can_manage_users': current_user.is_admin()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500