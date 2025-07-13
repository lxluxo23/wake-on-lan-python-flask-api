from flask import Blueprint, request, jsonify, session
from flask_bcrypt import Bcrypt
from functools import wraps
from wakeonlan import send_magic_packet
from app.models import User, Equipo, db
from app.utils import obtenerPorMac, ping

api = Blueprint('api', __name__, url_prefix='/api')
bcrypt = Bcrypt()

def api_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar si hay sesión activa
        if 'user_id' in session:
            return f(*args, **kwargs)
        
        # Verificar token en header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            # Verificar si el token tiene el formato esperado
            if token and token.startswith('token_'):
                # Extraer user_id del token (formato: token_1_admin)
                try:
                    user_id = int(token.split('_')[1])
                    # Verificar que el usuario existe en la base de datos
                    from app.models import User
                    user = User.query.get(user_id)
                    if user:
                        # Simular sesión para esta petición
                        session['user_id'] = user.id
                        return f(*args, **kwargs)
                except (ValueError, IndexError):
                    pass
        
        return jsonify({'error': 'No autorizado', 'message': 'Se requiere autenticación'}), 401
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
            session['user_id'] = user.id
            session['api_token'] = f"token_{user.id}_{username}"
            return jsonify({
                'success': True,
                'message': 'Login exitoso',
                'user': {
                    'id': user.id,
                    'username': user.username
                },
                'token': session['api_token']
            }), 200
        else:
            return jsonify({'error': 'Credenciales inválidas', 'message': 'Usuario o contraseña incorrectos'}), 401
    
    except Exception as e:
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/auth/logout', methods=['POST'])
@api_auth_required
def api_logout():
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
        new_user = User(username=username, password=hashed_password)
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
def api_get_equipos():
    try:
        equipos = Equipo.query.all()
        equipos_data = []
        
        for equipo in equipos:
            direccion_ip = obtenerPorMac(equipo.mac_address)
            estado = "desconocido"
            
            if direccion_ip:
                estado = "encendido" if ping(direccion_ip) else "apagado"
            
            equipos_data.append({
                'id': equipo.id,
                'nombre': equipo.nombre,
                'mac_address': equipo.mac_address,
                'ip_address': direccion_ip or "No disponible",
                'estado': estado
            })
        
        return jsonify({
            'success': True,
            'equipos': equipos_data,
            'total': len(equipos_data)
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/equipos', methods=['POST'])
@api_auth_required
def api_create_equipo():
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
        
        nuevo_equipo = Equipo(nombre=nombre, mac_address=mac_address)
        db.session.add(nuevo_equipo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Equipo creado exitosamente',
            'equipo': {
                'id': nuevo_equipo.id,
                'nombre': nuevo_equipo.nombre,
                'mac_address': nuevo_equipo.mac_address
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/equipos/<int:equipo_id>', methods=['GET'])
@api_auth_required
def api_get_equipo(equipo_id):
    try:
        equipo = Equipo.query.get(equipo_id)
        if not equipo:
            return jsonify({'error': 'No encontrado', 'message': 'Equipo no encontrado'}), 404
        
        direccion_ip = obtenerPorMac(equipo.mac_address)
        estado = "desconocido"
        
        if direccion_ip:
            estado = "encendido" if ping(direccion_ip) else "apagado"
        
        return jsonify({
            'success': True,
            'equipo': {
                'id': equipo.id,
                'nombre': equipo.nombre,
                'mac_address': equipo.mac_address,
                'ip_address': direccion_ip or "No disponible",
                'estado': estado
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/equipos/<int:equipo_id>', methods=['PUT'])
@api_auth_required
def api_update_equipo(equipo_id):
    try:
        equipo = Equipo.query.get(equipo_id)
        if not equipo:
            return jsonify({'error': 'No encontrado', 'message': 'Equipo no encontrado'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos inválidos', 'message': 'Se requiere JSON'}), 400
        
        nombre = data.get('nombre')
        mac_address = data.get('mac_address')
        
        if nombre:
            equipo.nombre = nombre
        
        if mac_address:
            mac_address = mac_address.upper()
            if not all(c in '0123456789ABCDEF:' for c in mac_address) or len(mac_address.replace(':', '')) != 12:
                return jsonify({'error': 'MAC inválida', 'message': 'Formato de dirección MAC inválido'}), 400
            
            existing_equipo = Equipo.query.filter_by(mac_address=mac_address).first()
            if existing_equipo and existing_equipo.id != equipo_id:
                return jsonify({'error': 'MAC duplicada', 'message': 'Ya existe otro equipo con esta dirección MAC'}), 409
            
            equipo.mac_address = mac_address
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Equipo actualizado exitosamente',
            'equipo': {
                'id': equipo.id,
                'nombre': equipo.nombre,
                'mac_address': equipo.mac_address
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/equipos/<int:equipo_id>', methods=['DELETE'])
@api_auth_required
def api_delete_equipo(equipo_id):
    try:
        equipo = Equipo.query.get(equipo_id)
        if not equipo:
            return jsonify({'error': 'No encontrado', 'message': 'Equipo no encontrado'}), 404
        
        db.session.delete(equipo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Equipo eliminado exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/equipos/<int:equipo_id>/encender', methods=['POST'])
@api_auth_required
def api_wake_equipo(equipo_id):
    try:
        equipo = Equipo.query.get(equipo_id)
        if not equipo:
            return jsonify({'error': 'No encontrado', 'message': 'Equipo no encontrado'}), 404
        
        send_magic_packet(equipo.mac_address)
        
        return jsonify({
            'success': True,
            'message': f'Señal de encendido enviada a {equipo.nombre}',
            'equipo': {
                'id': equipo.id,
                'nombre': equipo.nombre,
                'mac_address': equipo.mac_address
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Error interno', 'message': str(e)}), 500

@api.route('/equipos/<int:equipo_id>/estado', methods=['GET'])
@api_auth_required
def api_get_equipo_status(equipo_id):
    try:
        equipo = Equipo.query.get(equipo_id)
        if not equipo:
            return jsonify({'error': 'No encontrado', 'message': 'Equipo no encontrado'}), 404
        
        direccion_ip = obtenerPorMac(equipo.mac_address)
        estado = "desconocido"
        online = False
        
        if direccion_ip:
            online = ping(direccion_ip)
            estado = "encendido" if online else "apagado"
        
        return jsonify({
            'success': True,
            'equipo': {
                'id': equipo.id,
                'nombre': equipo.nombre,
                'mac_address': equipo.mac_address,
                'ip_address': direccion_ip or "No disponible",
                'estado': estado,
                'online': online
            }
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