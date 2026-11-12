"""Hace una serie fija de peticiones a la API y guarda las respuestas en un archivo.

Sirve para mostrar que la API responde igual antes y después del refactor.
Uso (con la API corriendo en otra terminal y sin avistamientos.db previo):

    python scripts/muestra_api.py docs/evidencias/antes_api.txt
"""

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("API_URL", "http://127.0.0.1:5000")
CARPETA_EJEMPLOS = os.path.join(os.path.dirname(__file__), "..", "ejemplos")

# (método, ruta, cuerpo). El cuerpo puede ser el nombre de un JSON de ejemplos/,
# un texto cualquiera o None.
PETICIONES = [
    ("GET", "/avistamientos", None),
    ("POST", "/avistamientos", "nuevo.json"),
    ("GET", "/avistamientos", None),
    ("GET", "/avistamientos/1", None),
    ("GET", "/avistamientos/999", None),
    ("POST", "/avistamientos", "incompleto.json"),
    ("POST", "/avistamientos", "esto no es json"),
    ("PUT", "/avistamientos/1", "actualizado.json"),
    ("PUT", "/avistamientos/999", "actualizado.json"),
    ("POST", "/avistamientos", "nuevo.json"),
    ("GET", "/avistamientos/resumen", None),
    ("DELETE", "/avistamientos/1", None),
    ("DELETE", "/avistamientos/1", None),
    ("GET", "/pajaros", None),
    ("PATCH", "/avistamientos", None),
]


def leer_cuerpo(cuerpo):
    if cuerpo is None:
        return None
    ruta = os.path.join(CARPETA_EJEMPLOS, cuerpo)
    if cuerpo.endswith(".json") and os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as archivo:
            return archivo.read().encode("utf-8")
    return cuerpo.encode("utf-8")


def hacer_peticion(metodo, ruta, cuerpo):
    datos = leer_cuerpo(cuerpo)
    peticion = urllib.request.Request(BASE + ruta, data=datos, method=metodo)
    if datos is not None:
        peticion.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(peticion) as respuesta:
            return respuesta.status, respuesta.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8")


def main():
    if len(sys.argv) != 2:
        print("Uso: python scripts/muestra_api.py <archivo_de_salida>")
        sys.exit(1)

    lineas = []
    for metodo, ruta, cuerpo in PETICIONES:
        estado, texto = hacer_peticion(metodo, ruta, cuerpo)
        try:
            texto = json.dumps(json.loads(texto), ensure_ascii=False, sort_keys=True)
        except ValueError:
            texto = texto.strip() or "(sin cuerpo)"
        enviado = f" con {cuerpo}" if cuerpo else ""
        lineas.append(f"{metodo} {ruta}{enviado}\n  -> {estado} {texto}\n")

    with open(sys.argv[1], "w", encoding="utf-8") as salida:
        salida.write("\n".join(lineas))
    print(f"Listo: {len(PETICIONES)} peticiones guardadas en {sys.argv[1]}")


if __name__ == "__main__":
    main()