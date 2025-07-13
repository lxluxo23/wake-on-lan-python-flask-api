from flask import Blueprint, flash, redirect, render_template, request, jsonify, session, url_for
from wakeonlan import send_magic_packet
from app.models import Equipo, db
from app.utils import obtenerPorMac, ping

main = Blueprint('main', __name__)

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

@main.route('/equipos', methods=['GET'])
def obtenerEquipos():
    equipos = Equipo.query.all()
    equipos_serializados = [equipo.serialize() for equipo in equipos]
    return jsonify(equipos_serializados)

@main.route('/equipos', methods=['POST'])
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

@main.route('/encender/<int:id>')
def encender_equipo(id):
    equipo = Equipo.query.get(id)
    if equipo:
        flash("Equipo encendido: {} (MAC: {})".format(equipo.nombre, equipo.mac_address), 'success')
        send_magic_packet(equipo.mac_address)
        return redirect(url_for('main.home'))
    else:
        return "Equipo no encontrado"