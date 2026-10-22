from datetime import date

import pytest

from validador import ValidadorDeAvistamiento


class RelojFijo:
    """Stub: un reloj que siempre responde la misma fecha."""

    def __init__(self, fecha):
        self._fecha = fecha

    def hoy(self):
        return self._fecha


@pytest.fixture
def validador():
    """Validador con el reloj fijo en 2026-06-15."""
    return ValidadorDeAvistamiento(RelojFijo(date(2026, 6, 15)))


def avistamiento(**cambios):
    """Avistamiento válido; cada prueba cambia solo el campo que le interesa."""
    datos = {
        "especie": "colibrí",
        "lugar": "Chingaza",
        "fecha": "2026-06-14",
        "observador": "Laura",
    }
    datos.update(cambios)
    return datos


# ---------- Datos completos ----------


def test_avistamiento_con_todos_los_datos_correctos_es_valido(validador):
    # Arrange
    datos = avistamiento()
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == {}


# ---------- Especie ----------


def test_especie_de_2_caracteres_es_invalida(validador):
    # Arrange
    datos = avistamiento(especie="ab")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert set(errores) == {"especie"}


def test_especie_de_3_caracteres_es_valida(validador):
    # Arrange
    datos = avistamiento(especie="abc")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == {}


def test_especie_de_50_caracteres_es_valida(validador):
    # Arrange
    datos = avistamiento(especie="a" * 50)
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == {}


def test_especie_de_51_caracteres_es_invalida(validador):
    # Arrange
    datos = avistamiento(especie="a" * 51)
    # Act
    errores = validador.validar(datos)
    # Assert
    assert set(errores) == {"especie"}


def test_especie_vacia_es_invalida_porque_es_obligatoria(validador):
    # Arrange
    datos = avistamiento(especie="")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert set(errores) == {"especie"}
    assert "obligatoria" in errores["especie"]


def test_especie_se_mide_sin_los_espacios_de_los_extremos(validador):
    # Arrange: con espacios mide 6, sin espacios mide 2
    datos = avistamiento(especie="  ab  ")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert set(errores) == {"especie"}


# ---------- Fecha (reloj fijo en 2026-06-15) ----------


def test_fecha_de_ayer_es_valida(validador):
    # Arrange
    datos = avistamiento(fecha="2026-06-14")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == {}


def test_fecha_de_hoy_es_valida(validador):
    # Arrange
    datos = avistamiento(fecha="2026-06-15")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert errores == {}


def test_fecha_de_manana_es_invalida_por_ser_posterior_a_hoy(validador):
    # Arrange
    datos = avistamiento(fecha="2026-06-16")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert set(errores) == {"fecha"}
    assert "posterior a hoy" in errores["fecha"]


def test_fecha_con_formato_dia_mes_anio_es_invalida(validador):
    # Arrange
    datos = avistamiento(fecha="15/06/2026")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert set(errores) == {"fecha"}
    assert "AAAA-MM-DD" in errores["fecha"]


def test_fecha_que_no_existe_en_el_calendario_es_invalida(validador):
    # Arrange: el 30 de febrero no existe
    datos = avistamiento(fecha="2026-02-30")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert set(errores) == {"fecha"}
    assert "no es una fecha válida" in errores["fecha"]


def test_fecha_vacia_es_invalida_porque_es_obligatoria(validador):
    # Arrange
    datos = avistamiento(fecha="")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert set(errores) == {"fecha"}
    assert "obligatoria" in errores["fecha"]


# ---------- Lugar, observador y cuerpo ----------


def test_lugar_con_solo_espacios_es_invalido(validador):
    # Arrange
    datos = avistamiento(lugar="   ")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert set(errores) == {"lugar"}


def test_observador_vacio_es_invalido(validador):
    # Arrange
    datos = avistamiento(observador="")
    # Act
    errores = validador.validar(datos)
    # Assert
    assert set(errores) == {"observador"}


def test_cuerpo_que_no_es_un_objeto_json_es_invalido(validador):
    # Arrange: una lista en vez de un objeto
    datos = ["colibrí", "Bogotá"]
    # Act
    errores = validador.validar(datos)
    # Assert
    assert set(errores) == {"cuerpo"}