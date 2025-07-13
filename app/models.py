from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Equipo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    mac_address = db.Column(db.String(17), unique=True, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'mac_address': self.mac_address
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password
        }