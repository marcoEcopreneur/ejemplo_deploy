from flask import render_template, redirect, request, session, flash
# Importamos las herramientas necesarias de Flask:
# - render_template: para mostrar páginas HTML
# - redirect: para enviar al usuario a otra ruta
# - request: para leer datos enviados desde formularios
# - session: para guardar datos del usuario mientras navega
# - flash: para mostrar mensajes cortos (errores, avisos)

from flask_app import app   # Importamos la app principal de Flask

from flask_app.models.usuario import Usuario  
# Importamos el modelo Usuario, para poder trabajar con la base de datos.

from werkzeug.security import generate_password_hash, check_password_hash
# Estas funciones sirven para encriptar contraseñas y compararlas de forma segura.


@app.route('/')
def index():
    # Esta es la ruta principal "/".
    # Si el usuario ya inició sesión, lo mandamos directo al inicio.
    if 'usuario_id' in session:
        return redirect('/inicio')
    # Si no ha iniciado sesión, lo mandamos a la página de login.
    return redirect('/entrar')


@app.route('/entrar')
def pagina_entrar():
    # Mostrar la página con los formularios de login y registro.
    return render_template('entrar.html')


@app.route('/registro', methods=['POST'])
def procesar_registro():
    # Este método procesa lo que el usuario envía desde el formulario de registro.

    # Primero validamos los datos usando la función del modelo Usuario.
    # Si algo está mal, vuelve a /entrar y se muestran los mensajes de error.
    if not Usuario.validar_registro(request.form):
        return redirect('/entrar')
    
    # Si la validación pasa, entonces encriptamos la contraseña.
    # Esto se hace para que NO se guarde en texto plano en la base de datos.
    password_encriptada = generate_password_hash(request.form['contrasena'])
    
    # Preparamos los datos tal como los espera el método guardar().
    data = {
        "nombre": request.form['nombre'],
        "apellido": request.form['apellido'],
        "email": request.form['email'],
        "contrasena": password_encriptada  # Guardamos la contraseña ya encriptada
    }

    # Guardamos el nuevo usuario en la base de datos.
    Usuario.guardar(data)

    # Mandamos un mensaje avisando que todo salió bien.
    flash("Registro exitoso. Ahora puede iniciar sesión.", "login")

    # Después de registrarse, lo devolvemos a la página para iniciar sesión.
    return redirect('/entrar')


@app.route('/login', methods=['POST'])
def procesar_login():
    # Este método procesa el formulario cuando el usuario intenta iniciar sesión.

    # Buscamos al usuario por su email en la base de datos.
    usuario = Usuario.obtener_por_email(request.form)

    # Si no existe, mostramos error y regresamos al login.
    if not usuario:
        flash("Email no encontrado", "login")
        return redirect('/entrar')
    
    # Si existe, comprobamos que la contraseña coincida con la encriptada.
    if not check_password_hash(usuario.contrasena, request.form['contrasena']):
        flash("Contraseña incorrecta", "login")
        return redirect('/entrar')
    
    # Si todo está bien, guardamos datos del usuario en la sesión.
    # Esto permite que permanezca "logueado".
    session['usuario_id'] = usuario.id
    session['nombre'] = usuario.nombre

    # Lo mandamos a la página de inicio.
    return redirect('/inicio')


@app.route('/salir')
def cerrar_sesion():
    # Esta ruta borra toda la información guardada en la sesión.
    # Es básicamente "cerrar sesión".
    session.clear()
    return redirect('/entrar')
