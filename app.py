"""Punto de arranque: arma el hexágono conectando cada puerto con su adaptador.

Es el único archivo que conoce a la vez la aplicación y todas las tecnologías.
Si mañana se cambia SQLite por otra base de datos, solo cambia este archivo y el
adaptador nuevo.
"""

import os

from avistamientos.adaptadores.primarios.api_flask import crear_app_flask
from avistamientos.adaptadores.secundarios.reloj_sistema import RelojSistema
from avistamientos.adaptadores.secundarios.repositorio_sqlite import RepositorioSqlite
from avistamientos.aplicacion.servicio import ServicioDeAvistamientos

CARPETA = os.path.dirname(os.path.abspath(__file__))


def create_app(config=None, reloj=None):
    configuracion = {"DATABASE": os.path.join(CARPETA, "avistamientos.db")}
    if config:
        configuracion.update(config)

    # Adaptadores secundarios (lo que la aplicación usa)
    repositorio = RepositorioSqlite(configuracion["DATABASE"])
    repositorio.crear_tabla()
    reloj = reloj or RelojSistema()

    # La aplicación (el hexágono) recibe sus puertos secundarios ya conectados
    servicio = ServicioDeAvistamientos(repositorio, reloj)

    # Adaptador primario (lo que usa la aplicación): la API web
    return crear_app_flask(servicio, configuracion)


if __name__ == "__main__":
    create_app().run(port=int(os.environ.get("PORT", 5000)))