from flask import Flask, render_template, request

app = Flask(__name__)

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
        return render_template('index.html', datos=mensajes_enviados)

@app.route('/lista_mensajes')
def lista_mensajes():
    # Llamar a la función recibir_datos para agregar datos a otra lista
    recibir_datos()
    return render_template('lista_mensajes.html', datos_formulario=mensajes_enviados, datos_otra_lista=mensajes_recibidos)

# Nueva función para recibir datos y añadirlos a otra lista
def recibir_datos():
    # Aquí puedes agregar valores quemados a la lista mensajes_recibidos
    mensajes_recibidos.append({'grupo': 'Grupo2', 'mensaje': 'Mensaje2'})
    mensajes_recibidos.append({'grupo': 'Grupo3', 'mensaje': 'Mensaje3'})

if __name__ == '__main__':
    app.run(debug=True)
