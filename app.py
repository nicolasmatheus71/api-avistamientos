import os

from flask import Flask, jsonify, request

import database
from avistamientos.aplicacion.validador import ValidadorDeAvistamiento
from reloj import RelojSistema

CAMPOS = ("especie", "lugar", "fecha", "observador")


def limpiar_datos(datos):
    """Devuelve solo los campos del avistamiento, sin espacios sobrantes."""
    return {campo: datos[campo].strip() for campo in CAMPOS}


def respuesta_datos_invalidos(errores):
    """Arma la respuesta 400 indicando qué campos fallaron y por qué."""
    mensaje = "Datos inválidos en: " + ", ".join(errores)
    return jsonify({"error": mensaje, "campos": errores}), 400


def create_app(config=None, reloj=None):
    app = Flask(__name__)
    app.json.ensure_ascii = False  # para que se vean las tildes (colibrí)
    app.config["DATABASE"] = os.path.join(app.root_path, "avistamientos.db")
    if config:
        app.config.update(config)

    validador = ValidadorDeAvistamiento(reloj or RelojSistema())

    app.teardown_appcontext(database.close_db)
    with app.app_context():
        database.init_db()

    @app.get("/avistamientos")
    def listar():
        return jsonify(database.listar_avistamientos()), 200

    @app.get("/avistamientos/resumen")
    def resumen():
        return jsonify(database.resumen_por_especie()), 200

    @app.get("/avistamientos/<int:avistamiento_id>")
    def ver(avistamiento_id):
        avistamiento = database.obtener_avistamiento(avistamiento_id)
        if avistamiento is None:
            return jsonify({"error": "Avistamiento no encontrado"}), 404
        return jsonify(avistamiento), 200

    @app.post("/avistamientos")
    def registrar():
        datos = request.get_json(silent=True)
        errores = validador.validar(datos)
        if errores:
            return respuesta_datos_invalidos(errores)
        nuevo = database.crear_avistamiento(**limpiar_datos(datos))
        return jsonify(nuevo), 201

    @app.put("/avistamientos/<int:avistamiento_id>")
    def actualizar(avistamiento_id):
        if database.obtener_avistamiento(avistamiento_id) is None:
            return jsonify({"error": "Avistamiento no encontrado"}), 404
        datos = request.get_json(silent=True)
        errores = validador.validar(datos)
        if errores:
            return respuesta_datos_invalidos(errores)
        actualizado = database.actualizar_avistamiento(
            avistamiento_id, **limpiar_datos(datos)
        )
        return jsonify(actualizado), 200

    @app.delete("/avistamientos/<int:avistamiento_id>")
    def eliminar(avistamiento_id):
        if not database.eliminar_avistamiento(avistamiento_id):
            return jsonify({"error": "Avistamiento no encontrado"}), 404
        return "", 204

    @app.errorhandler(404)
    def ruta_no_encontrada(error):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def metodo_no_permitido(error):
        return jsonify({"error": "Método no permitido"}), 405

    return app


if __name__ == "__main__":
    create_app().run(port=int(os.environ.get("PORT", 5000)))