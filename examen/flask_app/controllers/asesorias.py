from flask import render_template, redirect, request, session, flash
from flask_app import app
from flask_app.models.asesoria import Asesoria
from flask_app.models.usuario import Usuario

@app.route('/inicio')
def inicio():
    if 'usuario_id' not in session:
        return redirect('/entrar')
    
    # Obtener asesorías futuras
    asesorias = Asesoria.obtener_todas_futuras()
    return render_template('inicio.html', asesorias=asesorias)

@app.route('/nueva')
def vista_crear():
    if 'usuario_id' not in session:
        return redirect('/entrar')
    # BONUS: Enviar lista de usuarios para el selector de tutor
    Usuario.sembrar_tutores_si_faltan(session['usuario_id'], 3)
    tutores = Usuario.obtener_tutores_excepto({'id': session['usuario_id']})
    return render_template('crear.html', usuarios=tutores)

@app.route('/crear_asesoria', methods=['POST'])
def crear_asesoria():
    if 'usuario_id' not in session:
        return redirect('/entrar')

    if not Asesoria.validar_asesoria(request.form):
        return redirect('/nueva')

    tutor_raw = request.form.get('tutor_id', '')
    if tutor_raw == "":
        flash("Debe elegir un tutor.", "asesoria")
        return redirect('/nueva')
    tutor_id = int(tutor_raw)
    if tutor_id == session['usuario_id']:
        flash("El tutor no puede ser el creador.", "asesoria")
        return redirect('/nueva')

    data = {
        "tema": request.form['tema'],
        "fecha": request.form['fecha'],
        "duracion": request.form['duracion'],
        "notas": request.form['notas'],
        "usuario_id": session['usuario_id'],
        "tutor_id": tutor_id
    }
    Asesoria.guardar(data)
    return redirect('/inicio')

@app.route('/editar/<int:id>')
def vista_editar(id):
    if 'usuario_id' not in session:
        return redirect('/entrar')
    
    data = {"id": id}
    asesoria = Asesoria.obtener_una(data)
    
    # Validar que sea el creador
    if session['usuario_id'] != asesoria.usuario_id:
        return redirect('/inicio')

    Usuario.sembrar_tutores_si_faltan(asesoria.usuario_id, 3)
    tutores = Usuario.obtener_tutores_excepto({'id': asesoria.usuario_id})
    return render_template('editar.html', asesoria=asesoria, usuarios=tutores)

@app.route('/actualizar_asesoria', methods=['POST'])
def actualizar_asesoria():
    if 'usuario_id' not in session:
        return redirect('/entrar')

    if not Asesoria.validar_asesoria(request.form):
        return redirect(f"/editar/{request.form['id']}")

    original = Asesoria.obtener_una({"id": request.form['id']})
    tutor_raw = request.form.get('tutor_id', '')
    if tutor_raw == "":
        flash("Debe elegir un tutor.", "asesoria")
        return redirect(f"/editar/{request.form['id']}")
    tutor_id = int(tutor_raw)
    if tutor_id == original.usuario_id:
        flash("El tutor no puede ser el creador.", "asesoria")
        return redirect(f"/editar/{request.form['id']}")

    data = {
        "id": int(request.form['id']),
        "tema": request.form['tema'],
        "fecha": request.form['fecha'],
        "duracion": int(request.form['duracion']),
        "notas": request.form['notas'],
        "tutor_id": tutor_id
    }
    Asesoria.actualizar(data)
    return redirect('/inicio')

@app.route('/ver/<int:id>')
def ver_asesoria(id):
    if 'usuario_id' not in session:
        return redirect('/entrar')
    
    data = {"id": id}
    asesoria = Asesoria.obtener_una(data)
    Usuario.sembrar_tutores_si_faltan(asesoria.usuario_id, 3)
    tutores = Usuario.obtener_tutores_excepto({'id': asesoria.usuario_id})
    return render_template('ver.html', asesoria=asesoria, usuarios=tutores)

# BONUS: Ruta para cambiar tutor desde ver.html
@app.route('/cambiar_tutor', methods=['POST'])
def cambiar_tutor():
    if 'usuario_id' not in session:
        return redirect('/entrar')

    original = Asesoria.obtener_una({"id": request.form['id']})
    tutor_raw = request.form.get('tutor_id', '')
    if tutor_raw == "":
        flash("Debe elegir un tutor.", "asesoria")
        return redirect(f"/ver/{request.form['id']}")
    tutor_id = int(tutor_raw)
    if tutor_id == original.usuario_id:
        flash("El tutor no puede ser el creador.", "asesoria")
        return redirect(f"/ver/{request.form['id']}")

    Asesoria.actualizar_tutor({"id": int(request.form['id']), "tutor_id": tutor_id})
    return redirect(f"/ver/{request.form['id']}")

@app.route('/borrar/<int:id>')
def borrar_asesoria(id):
    if 'usuario_id' not in session:
        return redirect('/entrar')
    
    data = {"id": id}
    # Primero verificar que es el dueño (seguridad extra)
    asesoria = Asesoria.obtener_una(data)
    if session['usuario_id'] == asesoria.usuario_id:
        Asesoria.borrar(data)
        
    return redirect('/inicio')