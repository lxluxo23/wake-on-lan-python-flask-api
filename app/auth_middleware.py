from functools import wraps
from flask import request, jsonify, current_app
import jwt
from .models import User

def token_required(f):
    """Decorator para requerir token de autenticación"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Buscar token en headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer TOKEN
            except IndexError:
                return jsonify({'message': 'Token mal formateado'}), 401
        
        if not token:
            return jsonify({'message': 'Token faltante'}), 401
        
        try:
            # Decodificar token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
            
            if not current_user:
                return jsonify({'message': 'Token inválido'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator para requerir permisos de administrador"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Se requieren permisos de administrador',
                'error': 'insufficient_permissions'
            }), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def can_access_equipo(f):
    """Decorator para verificar acceso a equipo específico"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        # Obtener equipo_id de la URL o del JSON
        equipo_id = None
        
        # Intentar obtener de kwargs (parámetro de ruta)
        if 'equipo_id' in kwargs:
            equipo_id = kwargs['equipo_id']
        elif 'id' in kwargs:
            equipo_id = kwargs['id']
        # Intentar obtener del JSON del request
        elif request.is_json and request.json and 'id' in request.json:
            equipo_id = request.json['id']
        # Intentar obtener de form data
        elif 'id' in request.form:
            equipo_id = request.form['id']
        
        if not equipo_id:
            return jsonify({
                'success': False,
                'message': 'ID de equipo requerido',
                'error': 'missing_equipo_id'
            }), 400
        
        # Verificar acceso
        if not current_user.can_access_equipo(equipo_id):
            return jsonify({
                'success': False,
                'message': 'No tienes permisos para acceder a este equipo',
                'error': 'equipo_access_denied',
                'equipo_id': equipo_id
            }), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def role_required(*allowed_roles):
    """Decorator para requerir roles específicos"""
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if current_user.role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'message': f'Se requiere uno de estos roles: {", ".join(allowed_roles)}',
                    'error': 'insufficient_role',
                    'required_roles': allowed_roles,
                    'user_role': current_user.role
                }), 403
            
            return f(current_user, *args, **kwargs)
        
        return decorated
    return decorator

# Funciones de utilidad

def get_current_user_from_token():
    """Obtiene el usuario actual desde el token JWT"""
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return None
    
    if not token:
        return None
    
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return User.query.filter_by(id=data['user_id']).first()
    except:
        return None