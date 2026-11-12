import os

from flask import Flask, jsonify, request

from avistamientos.adaptadores.secundarios.reloj_sistema import RelojSistema
from avistamientos.adaptadores.secundarios.repositorio_sqlite import RepositorioSqlite
from avistamientos.aplicacion.errores import AvistamientoNoEncontrado, DatosInvalidos
from avistamientos.aplicacion.servicio import ServicioDeAvistamientos


def create_app(config=None, reloj=None):
    app = Flask(__name__)
    app.json.ensure_ascii = False  # para que se vean las tildes (colibrí)
    app.config["DATABASE"] = os.path.join(app.root_path, "avistamientos.db")
    if config:
        app.config.update(config)

    repositorio = RepositorioSqlite(app.config["DATABASE"])
    repositorio.crear_tabla()
    servicio = ServicioDeAvistamientos(repositorio, reloj or RelojSistema())

    @app.get("/avistamientos")
    def listar():
        return jsonify(servicio.listar()), 200

    @app.get("/avistamientos/resumen")
    def resumen():
        return jsonify(servicio.resumen_por_especie()), 200

    @app.get("/avistamientos/<int:avistamiento_id>")
    def ver(avistamiento_id):
        return jsonify(servicio.obtener(avistamiento_id)), 200

    @app.post("/avistamientos")
    def registrar():
        datos = request.get_json(silent=True)
        return jsonify(servicio.registrar(datos)), 201

    @app.put("/avistamientos/<int:avistamiento_id>")
    def actualizar(avistamiento_id):
        datos = request.get_json(silent=True)
        return jsonify(servicio.actualizar(avistamiento_id, datos)), 200

    @app.delete("/avistamientos/<int:avistamiento_id>")
    def eliminar(avistamiento_id):
        servicio.eliminar(avistamiento_id)
        return "", 204

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


if __name__ == "__main__":
    create_app().run(port=int(os.environ.get("PORT", 5000)))