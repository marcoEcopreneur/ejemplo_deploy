from flask import Flask, os
# Importamos la clase Flask desde el paquete flask.
# Flask es el framework que nos permite crear aplicaciones web de manera sencilla.

app = Flask(__name__)
# Aquí estamos creando una instancia de la aplicación Flask.
# "__name__" le dice a Flask dónde está el archivo principal para ubicar recursos y rutas.

app.secret_key = os.environ.get("SECRET_KEY", "dev")
# Esta es una clave secreta que Flask usa para:
# - Manejar sesiones
# - Proteger cookies
# - Evitar manipulaciones externas
# Debe mantenerse privada y normalmente se guarda en variables de entorno.

from flask_app.controllers import usuarios, asesorias
# Aquí importamos los controladores donde están definidas las rutas.
# Esto es importante porque al importar estos archivos, Flask “descubre” las rutas
# y las añade a la aplicación automáticamente.
# Sin esta línea, la app no sabría qué rutas existen.
