from flask import Blueprint, request, jsonify, session
from flask_bcrypt import Bcrypt
from functools import wraps
from wakeonlan import send_magic_packet
from app.models import User, Equipo, db
from app.utils import obtenerPorMac, ping
from app.auth_middleware import token_required, admin_required, can_access_equipo
import jwt
import datetime
from flask import current_app

api = Blueprint('api', __name__, url_prefix='/api')
bcrypt = Bcrypt()

def generate_token(user_id):
    """Generar token JWT para el usuario"""
    try:
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    except Exception as e:
        return None

def verify_token(token):
    """Verificar token JWT y retornar usuario"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        return User.query.get(user_id)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def api_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar token en header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No autorizado', 'message': 'Se requiere token de autenticación'}), 401
        
        token = auth_header.split(' ')[1]
        current_user = verify_token(token)
        
        if not current_user:
            return jsonify({'error': 'Token inválido', 'message': 'Token expirado o inválido'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated_function

def api_admin_required(f):
    @wraps(f)
    def decorated_function(current_user, *args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'error': 'Acceso denegado', 'message': 'Se requieren permisos de administrador'}), 403
        return f(current_user, *args, **kwargs)
    return decorated_function

def api_can_access_equipo(f):
    @wraps(f)
    def decorated_function(current_user, equipo_id, *args, **kwargs):
        if not current_user.is_admin() and not current_user.can_access_equipo(equipo_id):
            return jsonify({'error': 'Acceso denegado', 'message': 'No tiene permisos para acceder a este equipo'}), 403
        return f(current_user, equipo_id, *args, **kwargs)
    return decorated_function

@api.route('/auth/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos inválidos', 'message': 'Se requiere JSON'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Datos faltantes', 'message': 'Se requieren usuario y contraseña'}), 400
        
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            token = generate_token(user.id)
            if token:
                return jsonify({
                    'success': True,
                    'message': 'Login exitoso',
                    'user': user.serialize(),
                    'token': token
                }), 200
            else:
                return jsonify({'error': 'Error interno', 'message': 'No se pudo generar el token'}), 500
        else:
            return jsonify({'error': 'Credenciales inválidas', 'message': 'Usuario o contraseña incorrectos'}), 401
    
    except Exception as e:
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/auth/logout', methods=['POST'])
@api_auth_required
def api_logout(current_user):
    try:
        session.pop('user_id', None)
        session.pop('api_token', None)
        return jsonify({'success': True, 'message': 'Logout exitoso'}), 200
    except Exception as e:
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/auth/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos inválidos', 'message': 'Se requiere JSON'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Datos faltantes', 'message': 'Se requieren usuario y contraseña'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Contraseña débil', 'message': 'La contraseña debe tener al menos 6 caracteres'}), 400
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'Usuario existente', 'message': 'El nombre de usuario ya está en uso'}), 409
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password, role='user')
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuario registrado exitosamente',
            'user': {
                'id': new_user.id,
                'username': new_user.username
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/equipos', methods=['GET'])
@api_auth_required
def api_get_equipos(current_user):
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
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/equipos', methods=['POST'])
@api_auth_required
@api_admin_required
def api_create_equipo(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos inválidos', 'message': 'Se requiere JSON'}), 400
        
        nombre = data.get('nombre')
        mac_address = data.get('mac_address')
        
        if not nombre or not mac_address:
            return jsonify({'error': 'Datos faltantes', 'message': 'Se requieren nombre y dirección MAC'}), 400
        
        mac_address = mac_address.upper()
        if not all(c in '0123456789ABCDEF:' for c in mac_address) or len(mac_address.replace(':', '')) != 12:
            return jsonify({'error': 'MAC inválida', 'message': 'Formato de dirección MAC inválido'}), 400
        
        existing_equipo = Equipo.query.filter_by(mac_address=mac_address).first()
        if existing_equipo:
            return jsonify({'error': 'MAC duplicada', 'message': 'Ya existe un equipo con esta dirección MAC'}), 409
        
        nuevo_equipo = Equipo(
            nombre=nombre,
            descripcion=data.get('descripcion'),
            mac_address=mac_address.upper(),
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
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/equipos/<int:equipo_id>', methods=['GET'])
@api_auth_required
@api_can_access_equipo
def api_get_equipo(current_user, equipo_id):
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
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/equipos/<int:equipo_id>', methods=['PUT'])
@api_auth_required
@api_admin_required
def api_update_equipo(current_user, equipo_id):
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
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/equipos/<int:equipo_id>', methods=['DELETE'])
@api_auth_required
@api_admin_required
def api_delete_equipo(current_user, equipo_id):
    try:
        equipo = Equipo.query.get_or_404(equipo_id)
        nombre = equipo.nombre
        
        db.session.delete(equipo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Equipo {nombre} eliminado exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/equipos/<int:equipo_id>/encender', methods=['POST'])
@api_auth_required
@api_can_access_equipo
def api_wake_equipo(current_user, equipo_id):
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
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/equipos/<int:equipo_id>/estado', methods=['GET'])
@api_auth_required
@api_can_access_equipo
def api_get_equipo_status(current_user, equipo_id):
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
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/status', methods=['GET'])
def api_status():
    return jsonify({
        'success': True,
        'message': 'Wake-on-LAN API funcionando correctamente',
        'version': '1.0.0',
        'endpoints': {
            'auth': [
                'POST /api/auth/login',
                'POST /api/auth/logout', 
                'POST /api/auth/register'
            ],
            'equipos': [
                'GET /api/equipos',
                'POST /api/equipos',
                'GET /api/equipos/<id>',
                'PUT /api/equipos/<id>',
                'DELETE /api/equipos/<id>',
                'POST /api/equipos/<id>/encender',
                'GET /api/equipos/<id>/estado'
            ]
        }
    }), 200

# ============================================================================
# ENDPOINTS DE ADMINISTRACIÓN (solo admin)
# ============================================================================

@api.route('/admin/users', methods=['GET'])
@api_auth_required
@api_admin_required
def api_get_all_users(current_user):
    """Obtiene todos los usuarios (solo admin)"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'users': [user.serialize() for user in users],
            'total': len(users)
        })
    except Exception as e:
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/admin/users', methods=['POST'])
@api_auth_required
@api_admin_required
def api_create_user(current_user):
    """Crear nuevo usuario (solo admin)"""
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({
                'error': 'Datos faltantes',
                'message': 'Username y password son requeridos'
            }), 400
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'error': 'Usuario existente',
                'message': 'El usuario ya existe'
            }), 400
        
        # Crear usuario
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        nuevo_user = User(
            username=data['username'],
            password=hashed_password,
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
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/admin/assign-equipo', methods=['POST'])
@api_auth_required
@api_admin_required
def api_assign_equipo_to_user(current_user):
    """Asignar equipo a usuario (solo admin)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        equipo_id = data.get('equipo_id')
        
        if not user_id or not equipo_id:
            return jsonify({
                'error': 'Datos faltantes',
                'message': 'user_id y equipo_id son requeridos'
            }), 400
        
        user = User.query.get_or_404(user_id)
        equipo = Equipo.query.get_or_404(equipo_id)
        
        # Verificar si ya está asignado
        if equipo in user.equipos_asignados:
            return jsonify({
                'error': 'Equipo ya asignado',
                'message': f'El equipo {equipo.nombre} ya está asignado a {user.username}'
            }), 400
        
        # Asignar equipo
        user.equipos_asignados.append(equipo)
        
        # Los metadatos se pueden agregar directamente a la tabla user_equipos
        # por ahora solo hacemos la asignación básica
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Equipo {equipo.nombre} asignado a {user.username}',
            'user_id': user_id,
            'equipo_id': equipo_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/admin/unassign-equipo', methods=['POST'])
@api_auth_required
@api_admin_required
def api_unassign_equipo_from_user(current_user):
    """Desasignar equipo de usuario (solo admin)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        equipo_id = data.get('equipo_id')
        
        user = User.query.get_or_404(user_id)
        equipo = Equipo.query.get_or_404(equipo_id)
        
        if equipo not in user.equipos_asignados:
            return jsonify({
                'error': 'Equipo no asignado',
                'message': f'El equipo {equipo.nombre} no está asignado a {user.username}'
            }), 400
        
        # Desasignar equipo
        user.equipos_asignados.remove(equipo)
        
        # Los metadatos se eliminan automáticamente con la relación
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Equipo {equipo.nombre} desasignado de {user.username}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

# ============================================================================
# ENDPOINTS DE INFORMACIÓN DEL USUARIO
# ============================================================================

@api.route('/me', methods=['GET'])
@api_auth_required
def api_get_current_user_info(current_user):
    """Obtiene información del usuario actual"""
    try:
        equipos = current_user.get_equipos_permitidos()
        
        return jsonify({
            'success': True,
            'user': current_user.serialize(),
            'equipos_count': len(list(equipos)),
            'permissions': {
                'is_admin': current_user.is_admin(),
                'can_create_equipos': current_user.is_admin(),
                'can_manage_users': current_user.is_admin()
            }
        })
    except Exception as e:
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500