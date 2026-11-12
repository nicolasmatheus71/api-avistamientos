"""Pruebas del servicio (el hexágono) sin Flask y sin SQLite.

En vez de la base de datos real se usa un repositorio en memoria, que es otro
adaptador del mismo puerto. Esto solo es posible porque el servicio depende del
puerto y no de SQLite.
"""

from datetime import date

import pytest

from avistamientos.aplicacion.errores import AvistamientoNoEncontrado, DatosInvalidos
from avistamientos.aplicacion.puertos import RepositorioDeAvistamientos
from avistamientos.aplicacion.servicio import ServicioDeAvistamientos


class RelojFijo:
    """Stub: un reloj que siempre responde la misma fecha."""

    def __init__(self, fecha):
        self._fecha = fecha

    def hoy(self):
        return self._fecha


class RepositorioEnMemoria(RepositorioDeAvistamientos):
    """Fake: adaptador del puerto que guarda los avistamientos en un diccionario."""

    def __init__(self):
        self._datos = {}
        self._siguiente_id = 1

    def listar(self):
        return [self._datos[i] for i in sorted(self._datos)]

    def obtener(self, avistamiento_id):
        return self._datos.get(avistamiento_id)

    def crear(self, datos):
        nuevo = {"id": self._siguiente_id, **datos}
        self._datos[self._siguiente_id] = nuevo
        self._siguiente_id += 1
        return nuevo

    def actualizar(self, avistamiento_id, datos):
        if avistamiento_id not in self._datos:
            return None
        self._datos[avistamiento_id] = {"id": avistamiento_id, **datos}
        return self._datos[avistamiento_id]

    def eliminar(self, avistamiento_id):
        return self._datos.pop(avistamiento_id, None) is not None

    def resumen_por_especie(self):
        conteo = {}
        for avistamiento in self._datos.values():
            conteo[avistamiento["especie"]] = conteo.get(avistamiento["especie"], 0) + 1
        orden = sorted(conteo.items(), key=lambda par: (-par[1], par[0]))
        return [{"especie": especie, "cantidad": cantidad} for especie, cantidad in orden]


AVISTAMIENTO = {
    "especie": "colibrí",
    "lugar": "Bogotá",
    "fecha": "2026-06-14",
    "observador": "Laura",
}


@pytest.fixture
def repositorio():
    return RepositorioEnMemoria()


@pytest.fixture
def servicio(repositorio):
    """Servicio con repositorio en memoria y reloj fijo en 2026-06-15."""
    return ServicioDeAvistamientos(repositorio, RelojFijo(date(2026, 6, 15)))


def test_registrar_guarda_en_el_repositorio_y_devuelve_el_id(servicio, repositorio):
    # Act
    nuevo = servicio.registrar(AVISTAMIENTO)
    # Assert
    assert nuevo == {"id": 1, **AVISTAMIENTO}
    assert repositorio.listar() == [nuevo]


def test_registrar_quita_los_espacios_de_los_extremos(servicio):
    # Arrange
    datos = {**AVISTAMIENTO, "especie": "  colibrí  ", "lugar": " Bogotá "}
    # Act
    nuevo = servicio.registrar(datos)
    # Assert
    assert nuevo["especie"] == "colibrí"
    assert nuevo["lugar"] == "Bogotá"


def test_registrar_con_datos_invalidos_lanza_error_y_no_guarda(servicio, repositorio):
    # Arrange
    datos = {**AVISTAMIENTO, "fecha": "2026-06-16"}
    # Act
    with pytest.raises(DatosInvalidos) as error:
        servicio.registrar(datos)
    # Assert
    assert set(error.value.errores) == {"fecha"}
    assert repositorio.listar() == []


def test_obtener_inexistente_lanza_no_encontrado(servicio):
    # Act / Assert
    with pytest.raises(AvistamientoNoEncontrado):
        servicio.obtener(999)


def test_actualizar_reemplaza_los_datos(servicio):
    # Arrange
    servicio.registrar(AVISTAMIENTO)
    cambios = {**AVISTAMIENTO, "especie": "águila"}
    # Act
    actualizado = servicio.actualizar(1, cambios)
    # Assert
    assert actualizado == {"id": 1, **cambios}
    assert servicio.obtener(1)["especie"] == "águila"


def test_actualizar_inexistente_con_datos_invalidos_responde_primero_no_encontrado(servicio):
    # Arrange: el id no existe y además los datos son inválidos
    datos = {"especie": "ab"}
    # Act / Assert: primero se revisa que exista (igual que antes del refactor)
    with pytest.raises(AvistamientoNoEncontrado):
        servicio.actualizar(999, datos)


def test_eliminar_borra_y_eliminar_otra_vez_lanza_no_encontrado(servicio):
    # Arrange
    servicio.registrar(AVISTAMIENTO)
    # Act
    servicio.eliminar(1)
    # Assert
    assert servicio.listar() == []
    with pytest.raises(AvistamientoNoEncontrado):
        servicio.eliminar(1)


def test_resumen_cuenta_por_especie(servicio):
    # Arrange
    servicio.registrar(AVISTAMIENTO)
    servicio.registrar(AVISTAMIENTO)
    servicio.registrar({**AVISTAMIENTO, "especie": "águila"})
    # Act
    resumen = servicio.resumen_por_especie()
    # Assert
    assert resumen == [
        {"especie": "colibrí", "cantidad": 2},
        {"especie": "águila", "cantidad": 1},
    ]