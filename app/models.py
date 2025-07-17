from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Tabla de asociación simple para asignaciones usuario-equipo
user_equipos = db.Table('user_equipos',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('equipo_id', db.Integer, db.ForeignKey('equipo.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)  # 'admin' o 'user'
    
    # Relación muchos a muchos con equipos
    equipos_asignados = db.relationship('Equipo', 
                                       secondary=user_equipos, 
                                       backref=db.backref('usuarios_asignados', lazy='dynamic'),
                                       lazy='dynamic')

    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.role == 'admin'
    
    def can_access_equipo(self, equipo_id):
        """Verifica si el usuario puede acceder a un equipo específico"""
        if self.is_admin():
            return True
        return self.equipos_asignados.filter_by(id=equipo_id).first() is not None
    
    def get_equipos_permitidos(self):
        """Obtiene todos los equipos que el usuario puede acceder"""
        if self.is_admin():
            return Equipo.query.all()
        return self.equipos_asignados.all()

    def serialize(self, include_password=False):
        data = {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'equipos_count': self.equipos_asignados.count() if hasattr(self, 'equipos_asignados') else 0
        }
        if include_password:
            data['password'] = self.password
        return data

class Equipo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    mac_address = db.Column(db.String(17), unique=True, nullable=False)
    # Campos adicionales para el sistema de roles (opcionales)
    descripcion = db.Column(db.Text)
    ip_address = db.Column(db.String(15))
    estado = db.Column(db.String(20), default='desconocido')

    def get_usuarios_asignados(self):
        """Obtiene todos los usuarios asignados a este equipo"""
        return self.usuarios_asignados.all()
    
    def is_assigned_to_user(self, user_id):
        """Verifica si el equipo está asignado a un usuario específico"""
        return self.usuarios_asignados.filter_by(id=user_id).first() is not None

    def serialize(self, include_users=False):
        data = {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'mac_address': self.mac_address,
            'ip_address': self.ip_address,
            'estado': self.estado
        }
        
        if include_users:
            data['usuarios_asignados'] = [u.serialize() for u in self.get_usuarios_asignados()]
            data['usuarios_count'] = self.usuarios_asignados.count()
        
        return data

# Estructura final simplificada para producción:
# - user: id, username, password, role  
# - equipo: id, nombre, mac_address, descripcion?, ip_address?, estado?
# - user_equipos: user_id, equipo_id (tabla de asociación simple)