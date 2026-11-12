from flask import Flask, jsonify, request

from avistamientos.aplicacion.errores import AvistamientoNoEncontrado, DatosInvalidos
from avistamientos.aplicacion.puertos import PuertoDeAvistamientos


def crear_app_flask(puerto: PuertoDeAvistamientos, config=None):
    """Adaptador primario: traduce HTTP/JSON a llamadas al puerto y de vuelta.

    Aquí vive todo lo que es de la web: rutas, códigos de estado y mensajes de
    error en JSON. La regla de negocio no está aquí, está en el hexágono.
    """
    app = Flask(__name__)
    app.json.ensure_ascii = False  # para que se vean las tildes (colibrí)
    if config:
        app.config.update(config)

    @app.get("/avistamientos")
    def listar():
        return jsonify(puerto.listar()), 200

    @app.get("/avistamientos/resumen")
    def resumen():
        return jsonify(puerto.resumen_por_especie()), 200

    @app.get("/avistamientos/<int:avistamiento_id>")
    def ver(avistamiento_id):
        return jsonify(puerto.obtener(avistamiento_id)), 200

    @app.post("/avistamientos")
    def registrar():
        datos = request.get_json(silent=True)
        return jsonify(puerto.registrar(datos)), 201

    @app.put("/avistamientos/<int:avistamiento_id>")
    def actualizar(avistamiento_id):
        datos = request.get_json(silent=True)
        return jsonify(puerto.actualizar(avistamiento_id, datos)), 200

    @app.delete("/avistamientos/<int:avistamiento_id>")
    def eliminar(avistamiento_id):
        puerto.eliminar(avistamiento_id)
        return "", 204

    # ---------- Traducción de errores de la aplicación a HTTP ----------

    @app.errorhandler(AvistamientoNoEncontrado)
    def avistamiento_no_encontrado(error):
        return jsonify({"error": "Avistamiento no encontrado"}), 404

    @app.errorhandler(DatosInvalidos)
    def datos_invalidos(error):
        mensaje = "Datos inválidos en: " + ", ".join(error.errores)
        return jsonify({"error": mensaje, "campos": error.errores}), 400

    @app.errorhandler(404)
    def ruta_no_encontrada(error):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def metodo_no_permitido(error):
        return jsonify({"error": "Método no permitido"}), 405

    return app