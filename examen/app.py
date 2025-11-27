from flask_app import app     # Aquí estamos importando la variable 'app' desde el paquete 'flask_app'.
                              # 'app' normalmente es la aplicación Flask que configuraste en otro archivo.

if __name__ == "__main__":    # Esta línea verifica si este archivo se está ejecutando directamente.
                              # Es decir, si lo ejecutas como: python nombre_del_archivo.py
                              # y no si está siendo importado desde otro archivo.

    app.run(debug=True)       # Aquí iniciamos el servidor de Flask.
                              # 'debug=True' hace que la aplicación se reinicie sola cuando detecta cambios
                              # y también muestra mensajes de error más detallados (útil mientras estás aprendiendo).
