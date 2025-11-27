from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash, os
from datetime import datetime

class Asesoria:
    # Nombre de la base de datos que vamos a usar.
    db = os.environ.get("MYSQL_DB", "esquema_asesorias")

    def __init__(self, data):
        # Aquí recibimos un diccionario con los datos de la asesoría
        # y los guardamos en el objeto (self).
        self.id = data['id']
        self.tema = data['tema']
        self.fecha = data['fecha']
        self.duracion = data['duracion']
        self.notas = data['notas']
        self.usuario_id = data['usuario_id']
        self.tutor_id = data['tutor_id']

        # Estos son campos adicionales que vienen solo cuando usamos JOINS
        # y sirven para mostrar el nombre del creador y del tutor.
        self.creador_nombre = data.get('creador_nombre')  
        self.tutor_nombre = data.get('tutor_nombre')

    @classmethod
    def guardar(cls, data):
        # Inserta una nueva asesoría en la base de datos.
        query = """
            INSERT INTO asesorias (tema, fecha, duracion, notas, usuario_id, tutor_id) 
            VALUES (%(tema)s, %(fecha)s, %(duracion)s, %(notas)s, %(usuario_id)s, %(tutor_id)s);
        """
        # Ejecutamos la consulta usando el método que conecta con MySQL.
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def obtener_todas_futuras(cls):
        # Esta consulta hace un JOIN para unir asesorías con usuarios
        # y así poder mostrar el nombre del creador y del tutor.
        # También usamos CURDATE() para traer solo asesorías futuras o de hoy.
        query = """
            SELECT asesorias.*, 
                   CONCAT(creador.nombre, ' ', creador.apellido) as creador_nombre,
                   CONCAT(tutor.nombre, ' ', tutor.apellido) as tutor_nombre
            FROM asesorias
            JOIN usuarios as creador ON asesorias.usuario_id = creador.id
            LEFT JOIN usuarios as tutor ON asesorias.tutor_id = tutor.id
            WHERE asesorias.fecha >= CURDATE()
            ORDER BY asesorias.fecha ASC;
        """
        resultados = connectToMySQL(cls.db).query_db(query)

        # Convertimos cada fila en un objeto Asesoria.
        lista_asesorias = []
        if resultados:
            for fila in resultados:
                lista_asesorias.append(cls(fila))
        return lista_asesorias

    @classmethod
    def obtener_una(cls, data):
        # Trae una sola asesoría usando su ID.
        # También hace JOIN para mostrar nombres completos.
        query = """
            SELECT asesorias.*, 
                   CONCAT(creador.nombre, ' ', creador.apellido) as creador_nombre,
                   CONCAT(tutor.nombre, ' ', tutor.apellido) as tutor_nombre
            FROM asesorias
            JOIN usuarios as creador ON asesorias.usuario_id = creador.id
            LEFT JOIN usuarios as tutor ON asesorias.tutor_id = tutor.id
            WHERE asesorias.id = %(id)s;
        """
        resultado = connectToMySQL(cls.db).query_db(query, data)
        return cls(resultado[0])  # Creamos el objeto con la primera fila devuelta

    @classmethod
    def actualizar(cls, data):
        # Actualiza TODOS los campos de una asesoría existente.
        query = """
            UPDATE asesorias 
            SET tema=%(tema)s, fecha=%(fecha)s, duracion=%(duracion)s, notas=%(notas)s, tutor_id=%(tutor_id)s
            WHERE id = %(id)s;
        """
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def borrar(cls, data):
        # Elimina una asesoría por su ID.
        query = "DELETE FROM asesorias WHERE id = %(id)s;"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def actualizar_tutor(cls, data):
        # Solo cambia el tutor asociado a la asesoría.
        query = "UPDATE asesorias SET tutor_id=%(tutor_id)s WHERE id=%(id)s;"
        return connectToMySQL(cls.db).query_db(query, data)

    @staticmethod
    def validar_asesoria(formulario):
        # Esta función valida los datos del formulario antes de guardar o actualizar.
        es_valido = True

        # Obtenemos la fecha actual en formato YYYY-MM-DD para comparar.
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')

        # Validación del tema (no vacío)
        if len(formulario['tema']) < 1:
            flash("El tema es obligatorio.", "asesoria")
            es_valido = False
        
        # Validación de fecha
        if formulario['fecha'] == "":
            flash("La fecha es obligatoria.", "asesoria")
            es_valido = False
        elif formulario['fecha'] < fecha_hoy:
            # Validamos que la fecha no sea del pasado.
            flash("Por favor, seleccione una fecha válida (futura o actual)", "asesoria")
            es_valido = False
        
        # Validación de duración
        if formulario['duracion'] == "":
            flash("La duración es obligatoria.", "asesoria")
            es_valido = False
        else:
            # Convertimos duración a entero
            dur = int(formulario['duracion'])
            # Revisamos que esté entre 1 y 8 horas.
            if dur < 1 or dur > 8:
                flash("La duración debe ser entre 1 y 8 horas.", "asesoria")
                es_valido = False
        
        # Validación de notas
        if len(formulario['notas']) < 1:
            flash("Las notas no pueden estar vacías.", "asesoria")
            es_valido = False
        elif len(formulario['notas']) > 50:
            # Máximo de caracteres permitido
            flash("Las notas no pueden tener más de 50 caracteres.", "asesoria")
            es_valido = False
        
        # Validación del tutor seleccionado
        if formulario.get('tutor_id', '') == "":
            flash("Debe elegir un tutor.", "asesoria")
            es_valido = False
            
        return es_valido
