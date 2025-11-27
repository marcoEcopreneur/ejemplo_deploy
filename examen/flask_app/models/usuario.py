from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re
import datetime
from werkzeug.security import generate_password_hash

# Expresión regular para validar formato de email.
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class Usuario:
    # Nombre de la base de datos
    db = "esquema_asesorias"

    def __init__(self, data):
        # Constructor que recibe un diccionario con datos de la DB
        self.id = data['id']
        self.nombre = data['nombre']
        self.apellido = data['apellido']
        self.email = data['email']
        self.contrasena = data['contrasena']

    # ----------------------------------------------------------------------
    # Crear un usuario normal
    # ----------------------------------------------------------------------
    @classmethod
    def guardar(cls, data):
        query = "INSERT INTO usuarios (nombre, apellido, email, contrasena) VALUES (%(nombre)s, %(apellido)s, %(email)s, %(contrasena)s);"
        return connectToMySQL(cls.db).query_db(query, data)

    # ----------------------------------------------------------------------
    # Buscar usuario por email (se usa para login y validación de registro)
    # ----------------------------------------------------------------------
    @classmethod
    def obtener_por_email(cls, data):
        query = "SELECT * FROM usuarios WHERE email = %(email)s;"
        resultado = connectToMySQL(cls.db).query_db(query, data)
        if len(resultado) < 1:
            return False
        return cls(resultado[0])

    # ----------------------------------------------------------------------
    # Obtener usuario por ID
    # ----------------------------------------------------------------------
    @classmethod
    def obtener_por_id(cls, data):
        query = "SELECT * FROM usuarios WHERE id = %(id)s;"
        resultado = connectToMySQL(cls.db).query_db(query, data)
        return cls(resultado[0])
    
    # ----------------------------------------------------------------------
    # Obtener todos los usuarios (útil para el selector de tutores)
    # ----------------------------------------------------------------------
    @classmethod
    def obtener_todos(cls):
        query = "SELECT * FROM usuarios;"
        resultados = connectToMySQL(cls.db).query_db(query)
        usuarios = []
        for fila in resultados:
            usuarios.append(cls(fila))
        return usuarios

    # ----------------------------------------------------------------------
    # Verifica si la columna 'es_tutor' existe; si no, la añade automáticamente
    # ----------------------------------------------------------------------
    @classmethod
    def ensure_tutor_column(cls):
        try:
            check = connectToMySQL(cls.db).query_db(
                "SELECT COUNT(*) AS c FROM information_schema.columns WHERE table_schema=%(schema)s AND table_name='usuarios' AND column_name='es_tutor';",
                {"schema": cls.db}
            )
            # Si no existe, agregar la columna
            if not check or check[0]["c"] == 0:
                connectToMySQL(cls.db).query_db("ALTER TABLE usuarios ADD COLUMN es_tutor TINYINT(1) NOT NULL DEFAULT 0;")
        except:
            # En caso de error, simplemente ignora (no rompe la app)
            pass

    # ----------------------------------------------------------------------
    # Obtener lista de tutores, excluyendo al usuario actual
    # ----------------------------------------------------------------------
    @classmethod
    def obtener_tutores_excepto(cls, data):
        cls.ensure_tutor_column()
        query = "SELECT * FROM usuarios WHERE es_tutor = 1 AND id != %(id)s;"
        resultados = connectToMySQL(cls.db).query_db(query, data)
        usuarios = []
        for fila in resultados or []:
            usuarios.append(cls(fila))
        return usuarios

    # ----------------------------------------------------------------------
    # Contar cuántos tutores existen, excluyendo al usuario actual
    # ----------------------------------------------------------------------
    @classmethod
    def contar_tutores_excepto(cls, data):
        cls.ensure_tutor_column()
        query = "SELECT COUNT(*) AS c FROM usuarios WHERE es_tutor = 1 AND id != %(id)s;"
        res = connectToMySQL(cls.db).query_db(query, data)
        return res[0]['c'] if res else 0

    # ----------------------------------------------------------------------
    # Crear un usuario tutor (es_tutor = 1)
    # ----------------------------------------------------------------------
    @classmethod
    def guardar_tutor(cls, data):
        query = "INSERT INTO usuarios (nombre, apellido, email, contrasena, es_tutor) VALUES (%(nombre)s, %(apellido)s, %(email)s, %(contrasena)s, 1);"
        return connectToMySQL(cls.db).query_db(query, data)

    # ----------------------------------------------------------------------
    # Se asegura que existan al menos N tutores (útil para que el sistema no quede vacío)
    # Genera tutores falsos si el número es menor al mínimo requerido.
    # ----------------------------------------------------------------------
    @classmethod
    def sembrar_tutores_si_faltan(cls, exclude_id, minimo=3):
        cls.ensure_tutor_column()
        actual = cls.contar_tutores_excepto({'id': exclude_id})

        # Si ya hay suficientes tutores, no hacer nada
        if actual >= minimo:
            return

        # Nombres base para crear tutores automáticos
        base = [
            ("Juan", "Pérez"),
            ("María", "González"),
            ("Carlos", "Ramírez"),
            ("Lucía", "Martínez"),
            ("Pedro", "López"),
            ("Ana", "Torres")
        ]
        faltan = minimo - actual

        # Se usa timestamp para evitar colisiones de correo
        ts = int(datetime.datetime.utcnow().timestamp())

        for i in range(faltan):
            nombre, apellido = base[i % len(base)]
            email = f"tutor_{ts}_{i}@ejemplo.com"
            data = {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'contrasena': generate_password_hash('123456')
            }
            cls.guardar_tutor(data)

    # ----------------------------------------------------------------------
    # Validación del formulario de registro
    # Se dispara antes de guardar un usuario nuevo.
    # ----------------------------------------------------------------------
    @staticmethod
    def validar_registro(usuario):
        es_valido = True

        # Nombre mínimo 1 carácter
        if len(usuario['nombre']) < 1:
            flash("El nombre debe tener al menos 1 caracteres.", "registro")
            es_valido = False

        # Apellido mínimo 2 caracteres
        if len(usuario['apellido'].strip()) < 2:
            flash("El apellido debe tener al menos 2 caracteres.", "registro")
            es_valido = False

        # Email con regex
        if not EMAIL_REGEX.match(usuario['email']):
            flash("Email inválido.", "registro")
            es_valido = False

        # Validar que el email no esté ya registrado
        datos_email = {'email': usuario['email']}
        if Usuario.obtener_por_email(datos_email):
            flash("Ese email ya está registrado.", "registro")
            es_valido = False

        # Contraseña mínima 3 caracteres
        if len(usuario['contrasena']) < 3:
            flash("La contraseña debe tener al menos 3 caracteres.", "registro")
            es_valido = False

        # Contraseña debe coincidir con confirmación
        if usuario['contrasena'] != usuario['confirmar_contrasena']:
            flash("Las contraseñas no coinciden.", "registro")
            es_valido = False

        return es_valido
