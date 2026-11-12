"""Revisa la dirección de las dependencias: el hexágono no puede importar el exterior."""

import ast
from pathlib import Path

CARPETA_APLICACION = Path(__file__).parent.parent / "avistamientos" / "aplicacion"
PROHIBIDOS = ("flask", "sqlite3", "avistamientos.adaptadores", "app")


def modulos_importados(archivo):
    arbol = ast.parse(archivo.read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            yield from (alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            yield nodo.module


def test_la_aplicacion_no_depende_de_flask_sqlite_ni_adaptadores():
    # Arrange
    archivos = list(CARPETA_APLICACION.glob("*.py"))
    # Act
    violaciones = [
        f"{archivo.name} importa {modulo}"
        for archivo in archivos
        for modulo in modulos_importados(archivo)
        if any(modulo == p or modulo.startswith(p + ".") for p in PROHIBIDOS)
    ]
    # Assert
    assert archivos, "no se encontraron archivos en avistamientos/aplicacion"
    assert violaciones == []