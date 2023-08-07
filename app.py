from flask import Flask, flash, redirect, render_template, request, jsonify,session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from wakeonlan import send_magic_packet
import platform   
import subprocess 

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

app = Flask(__name__)
app.secret_key = '7689myc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///equipos.db'
app.config['DEBUG'] = False
app.config['SQLALCHEMY_ECHO'] = False
CORS(app)
db = SQLAlchemy(app) 
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

def obtenerPorMac(mac_address):
    mac_address= formatearMac(mac_address)
    try:
        result = subprocess.check_output(['arp', '-a'], shell=True, text=True)
        for line in result.split('\n'):
            if mac_address in line:
                parts = line.split()
                ip_address = parts[0]
                return ip_address
    except subprocess.CalledProcessError:
        return None
    
def formatearMac(mac):
    mac_formateada = mac.replace(':', '-')
    return mac_formateada.lower()

def ping(host):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', host]
    return subprocess.call(command) == 0

class Equipo(db.Model):
    id = db.Column(db.Integer , primary_key=True)
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
@app.route('/')
def home():
    equipos = Equipo.query.all()
    resultados = []
    for equipo in equipos:
        direccion_ip = obtenerPorMac(equipo.mac_address)
        if direccion_ip:
            estado = "Encendido" if ping(direccion_ip) else "Apagado"
            resultados.append({
                'id':equipo.id,
                'nombre': equipo.nombre,
                'mac_address': equipo.mac_address,
                'ip_address': direccion_ip,
                'estado': estado
            })
        else:
            resultados.append({
                'id':equipo.id,
                'nombre': equipo.nombre,
                'mac_address': equipo.mac_address,
                'ip_address': "No disponible",
                'estado': "Desconocido"
            })
    return render_template ('index.html',resultados=resultados)
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        session['user_id'] = user.id  # Iniciar sesión
        return jsonify({'message': 'Inicio de sesión exitoso'}), 200
    else:
        return jsonify({'message': 'Credenciales incorrectas'}), 401

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'message': 'Se requieren nombre de usuario y contraseña'}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'El nombre de usuario ya está en uso'}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Usuario registrado exitosamente'}), 201

@app.route('/equipos',methods=['GET'])
def obtenerEquipos():
    equipos = Equipo.query.all()
    equipos_serializados = [equipo.serialize() for equipo in equipos]
    return jsonify(equipos_serializados)

@app.route('/equipos', methods=['POST'])
def agrgarEquipo():
    data = request.get_json()
    nombre = data.get('nombre')
    mac_address = data.get('mac_address')
    if not nombre or not mac_address:
        return jsonify({"error": "Nombre y dirección MAC son obligatorios"}), 400
    nuevo_equipo = Equipo(nombre=nombre, mac_address=mac_address)
    try:
        db.session.add(nuevo_equipo)
        db.session.commit()
        return jsonify({"message": "Equipo agregado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/encender/<int:id>')
def encender_equipo(id):
    equipo = Equipo.query.get(id)
    if equipo:
        flash("Equipo encendido: {} (MAC: {})".format(equipo.nombre, equipo.mac_address), 'success')
        send_magic_packet(equipo.mac_address)
        return redirect(url_for('home'))
    else:
        return "Equipo no encontrado"
if __name__ == '__main__':
    app.run(debug=False)
