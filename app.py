from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

import json
import socket
from serial import Serial

app = Flask(__name__)
# app.config['SERIAL_BAUDRATE'] = 9600
# app.config['SERIAL_TIMEOUT'] = 0.1
# app.config['SERIAL_PORT'] = 'COM1'  # CP2102 port


# no touching
default_baudrate = 115200
default_timeout = 1
port_name = 'COM6'
socketio = SocketIO(app)

ser = None
i = 0


def connect_port():
    global ser, i
    try:
        ser = Serial(port_name, default_baudrate)
        ser.open()
        i = 0
        # socketio.emit('message', {'message': 'Connected'})
    except Exception as e:
        print(e)
        # socketio.emit(
#            'message', {'messa': 'Port does not exist, check the communication port...'})


@socketio.on('disconnect')
def disconnect_port():
    global ser
    if ser and ser.is_open:
        ser.close()
        socketio.emit('message', {'message': 'Disconnected'})
    else:
        socketio.emit('message', {'message': 'Port is not open...'})


@socketio.on('send_user_message')
def send_user_message(message):
    socketio.emit('display_processed_message', {'message': message})
    print('display_processed_message: ', message)
    # Send the processed message to Raspberry Pico
    ser.write(message.encode('utf-8'))


@socketio.on('read_message')
def read_message():
    global i
    while True:
        if ser and ser.is_open:
            if ser.in_waiting > 0:
                serial_reading = ser.readline().decode('UTF-8').rstrip()
                i += 1
                socketio.emit('message', {'message': serial_reading})


# Listas globales para almacenar los datos
mensajes_enviados = []
mensajes_recibidos = []


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html', datos=mensajes_enviados)


@app.route('/enviar', methods=['POST'])
def enviar():
    global i
    if request.method == 'POST':
        grupo = request.form['grupo']
        mensaje = request.form['mensaje']
        # Almacenar los datos en la lista global (formulario)
        mensajes_enviados.append({'grupo': grupo, 'mensaje': mensaje})
        # -------------------------------------------------------
        message_prelim = grupo + "|" + mensaje + "|" + str(i)
        message_prelim = message_prelim.strip()
        message = message_prelim + "\n"
        encoded_message = message.encode('utf-8')

        # levantasion del socket
        HOST = '127.0.0.1'
        PORT = 7070
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(encoded_message)

        # ser.write(encoded_message)
        socketio.emit('send_user_message', {'message': message})
        # -------------------------------------------------------
        return render_template('index.html', datos=mensajes_enviados)


@app.route('/lista_mensajes')
def lista_mensajes():
    # Llamar a la función recibir_datos para agregar datos a otra lista
    return render_template('lista_mensajes.html', datos_formulario=mensajes_enviados, datos_otra_lista=mensajes_recibidos)

# Nueva función para recibir datos y añadirlos a otra lista


@app.route('/received_router_message', methods=['POST'])
def received_router_message():
    data = request.json

    if 'message' in data:
        message = data['message']
        # Trigger Socket.IO event
        socketio.emit('router_message', {
                      'message': message}, namespace='/test')
        mensajes_recibidos.append({'grupo': 'Grupo X', 'mensaje': message})

        return jsonify({'status': 'success', 'message': 'Message received and Socket.IO event triggered'})
    else:
        return jsonify({'status': 'error', 'message': 'No "message" property found in the JSON data'})


def recibir_datos():
    # -------------------------------------------------------

    # -------------------------------------------------------
    # Agregar valores quemados a la lista mensajes_recibidos
    mensajes_recibidos.append({'grupo': 'Grupo2', 'mensaje': 'Mensaje2'})
    mensajes_recibidos.append({'grupo': 'Grupo3', 'mensaje': 'Mensaje3'})


# connect_port()
if __name__ == '__main__':
    socketio.run(app, debug=False)
