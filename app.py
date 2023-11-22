from flask import Flask, render_template, request
from flask_serial import Serial
from flask_socketio import SocketIO

import json
import serial
import threading


import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SERIAL_BAUDRATE'] = 9600
app.config['SERIAL_TIMEOUT'] = 0.1
app.config['SERIAL_PORT'] = 'COM1' # CP2102 port


# no touching
default_baudrate = app.config['SERIAL_BAUDRATE']
default_timeout = app.config['SERIAL_TIMEOUT']
port_name = app.config['SERIAL_PORT']

ser = Serial(app)
socketio = SocketIO(app)

ser = None
i = 0


@socketio.on('connect')
def connect_port(data):
    global ser, i
    try:
        ser = serial.Serial(port_name, default_baudrate, default_timeout)
        i = 0
        thread = threading.Thread(target=read_message)
        thread.daemon = True
        thread.start()
        socketio.emit('message', {'message': 'Connected'})
    except serial.SerialException:
        socketio.emit('message', {'messa': 'Port does not exist, check the communication port...'})

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

@app.route('/')
def home():
    return render_template('index.html', datos=mensajes_enviados)

@app.route('/enviar', methods=['POST'])
def enviar():
    if request.method == 'POST':
        grupo = request.form['grupo']
        mensaje = request.form['mensaje']
        # Almacenar los datos en la lista global (formulario)
        mensajes_enviados.append({'grupo': grupo, 'mensaje': mensaje})
        # ------------------------------------------------------- 
        message_prelim = grupo + "|" + mensaje
        message_prelim = message_prelim.strip()
        message = message_prelim + "\n"
        socketio.emit('send_user_message', {'message': message})
        # -------------------------------------------------------
        return render_template('index.html', datos=mensajes_enviados)

@app.route('/lista_mensajes')
def lista_mensajes():
    # Llamar a la función recibir_datos para agregar datos a otra lista
    recibir_datos()
    return render_template('lista_mensajes.html', datos_formulario=mensajes_enviados, datos_otra_lista=mensajes_recibidos)

# Nueva función para recibir datos y añadirlos a otra lista
def recibir_datos():
    # -------------------------------------------------------
    
    # -------------------------------------------------------
    # Agregar valores quemados a la lista mensajes_recibidos
    mensajes_recibidos.append({'grupo': 'Grupo2', 'mensaje': 'Mensaje2'})
    mensajes_recibidos.append({'grupo': 'Grupo3', 'mensaje': 'Mensaje3'})


if __name__ == '__main__':
    socketio.run(app, debug=False)