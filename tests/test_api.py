from datetime import date

import pytest

from app import create_app


class RelojFijo:
    """Stub: un reloj que siempre responde la misma fecha (15 de junio de 2026)."""

    def __init__(self, fecha):
        self._fecha = fecha

    def hoy(self):
        return self._fecha


AVISTAMIENTO = {
    "especie": "colibrí",
    "lugar": "Bogotá",
    "fecha": "2026-06-14",
    "observador": "Laura",
}


@pytest.fixture
def client(tmp_path):
    """Cliente de pruebas con base de datos temporal y vacía, y con el reloj fijo."""
    reloj = RelojFijo(date(2026, 6, 15))
    app = create_app(
        {"DATABASE": str(tmp_path / "prueba.db"), "TESTING": True}, reloj=reloj
    )
    return app.test_client()


def crear(client, **cambios):
    """Registra un avistamiento válido (cambiando solo lo que se indique)."""
    return client.post("/avistamientos", json={**AVISTAMIENTO, **cambios})


# ---------- GET /avistamientos ----------


def test_listar_sin_avistamientos_responde_200_y_lista_vacia(client):
    # Arrange: base de datos vacía
    # Act
    respuesta = client.get("/avistamientos")
    # Assert
    assert respuesta.status_code == 200
    assert respuesta.get_json() == []


def test_listar_responde_200_con_los_avistamientos_registrados(client):
    # Arrange
    crear(client)
    crear(client, especie="águila")
    # Act
    respuesta = client.get("/avistamientos")
    # Assert
    assert respuesta.status_code == 200
    lista = respuesta.get_json()
    assert [a["id"] for a in lista] == [1, 2]
    assert [a["especie"] for a in lista] == ["colibrí", "águila"]


# ---------- GET /avistamientos/{id} ----------


def test_ver_avistamiento_existente_responde_200_con_todos_sus_campos(client):
    # Arrange
    crear(client)
    # Act
    respuesta = client.get("/avistamientos/1")
    # Assert
    assert respuesta.status_code == 200
    assert respuesta.get_json() == {"id": 1, **AVISTAMIENTO}


def test_ver_avistamiento_inexistente_responde_404_con_mensaje(client):
    # Arrange: base de datos vacía
    # Act
    respuesta = client.get("/avistamientos/999")
    # Assert
    assert respuesta.status_code == 404
    assert "no encontrado" in respuesta.get_json()["error"]


# ---------- POST /avistamientos ----------


def test_registrar_responde_201_con_el_avistamiento_creado(client):
    # Arrange: base de datos vacía
    # Act
    respuesta = crear(client)
    # Assert
    assert respuesta.status_code == 201
    assert respuesta.get_json() == {"id": 1, **AVISTAMIENTO}


def test_registrar_guarda_el_avistamiento_y_se_puede_consultar_con_get(client):
    # Arrange
    nuevo = crear(client).get_json()
    # Act
    respuesta = client.get(f"/avistamientos/{nuevo['id']}")
    # Assert
    assert respuesta.status_code == 200
    assert respuesta.get_json() == nuevo


def test_registrar_con_datos_incompletos_responde_400_e_indica_los_campos(client):
    # Arrange
    datos = {"especie": "colibrí"}
    # Act
    respuesta = client.post("/avistamientos", json=datos)
    # Assert
    assert respuesta.status_code == 400
    cuerpo = respuesta.get_json()
    assert set(cuerpo["campos"]) == {"lugar", "fecha", "observador"}
    assert "lugar" in cuerpo["error"]


def test_registrar_con_especie_de_2_caracteres_responde_400_y_no_guarda(client):
    # Arrange
    datos = {**AVISTAMIENTO, "especie": "ab"}
    # Act
    respuesta = client.post("/avistamientos", json=datos)
    # Assert
    assert respuesta.status_code == 400
    assert set(respuesta.get_json()["campos"]) == {"especie"}
    assert client.get("/avistamientos").get_json() == []


def test_registrar_con_fecha_de_manana_responde_400(client):
    # Arrange: el reloj fijo marca 2026-06-15, mañana es 2026-06-16
    datos = {**AVISTAMIENTO, "fecha": "2026-06-16"}
    # Act
    respuesta = client.post("/avistamientos", json=datos)
    # Assert
    assert respuesta.status_code == 400
    assert set(respuesta.get_json()["campos"]) == {"fecha"}


def test_registrar_con_fecha_de_hoy_responde_201(client):
    # Arrange: el reloj fijo marca 2026-06-15
    datos = {**AVISTAMIENTO, "fecha": "2026-06-15"}
    # Act
    respuesta = client.post("/avistamientos", json=datos)
    # Assert
    assert respuesta.status_code == 201
    assert respuesta.get_json()["fecha"] == "2026-06-15"


def test_registrar_con_cuerpo_que_no_es_json_responde_400(client):
    # Arrange
    texto = "esto no es json"
    # Act
    respuesta = client.post(
        "/avistamientos", data=texto, content_type="application/json"
    )
    # Assert
    assert respuesta.status_code == 400
    assert "cuerpo" in respuesta.get_json()["campos"]


# ---------- PUT /avistamientos/{id} ----------


def test_actualizar_responde_200_con_los_datos_nuevos_y_los_guarda(client):
    # Arrange
    crear(client)
    cambios = {
        "especie": "águila",
        "lugar": "Chingaza",
        "fecha": "2026-06-10",
        "observador": "Mateo",
    }
    # Act
    respuesta = client.put("/avistamientos/1", json=cambios)
    # Assert
    assert respuesta.status_code == 200
    assert respuesta.get_json() == {"id": 1, **cambios}
    assert client.get("/avistamientos/1").get_json() == {"id": 1, **cambios}


def test_actualizar_avistamiento_inexistente_responde_404(client):
    # Arrange: base de datos vacía
    # Act
    respuesta = client.put("/avistamientos/999", json=AVISTAMIENTO)
    # Assert
    assert respuesta.status_code == 404


def test_actualizar_con_datos_invalidos_responde_400_y_no_cambia_el_registro(client):
    # Arrange
    crear(client)
    datos = {**AVISTAMIENTO, "fecha": "2026-06-16"}
    # Act
    respuesta = client.put("/avistamientos/1", json=datos)
    # Assert
    assert respuesta.status_code == 400
    assert set(respuesta.get_json()["campos"]) == {"fecha"}
    assert client.get("/avistamientos/1").get_json() == {"id": 1, **AVISTAMIENTO}


# ---------- DELETE /avistamientos/{id} ----------


def test_eliminar_responde_204_sin_cuerpo_y_el_avistamiento_deja_de_existir(client):
    # Arrange
    crear(client)
    # Act
    respuesta = client.delete("/avistamientos/1")
    # Assert
    assert respuesta.status_code == 204
    assert respuesta.data == b""
    assert client.get("/avistamientos/1").status_code == 404
    assert client.get("/avistamientos").get_json() == []


def test_eliminar_avistamiento_inexistente_responde_404(client):
    # Arrange: base de datos vacía
    # Act
    respuesta = client.delete("/avistamientos/999")
    # Assert
    assert respuesta.status_code == 404


# ---------- GET /avistamientos/resumen ----------


def test_resumen_cuenta_los_avistamientos_por_especie(client):
    # Arrange
    crear(client)
    crear(client)
    crear(client, especie="águila")
    # Act
    respuesta = client.get("/avistamientos/resumen")
    # Assert
    assert respuesta.status_code == 200
    assert respuesta.get_json() == [
        {"cantidad": 2, "especie": "colibrí"},
        {"cantidad": 1, "especie": "águila"},
    ]


def test_resumen_sin_avistamientos_responde_200_y_lista_vacia(client):
    # Arrange: base de datos vacía
    # Act
    respuesta = client.get("/avistamientos/resumen")
    # Assert
    assert respuesta.status_code == 200
    assert respuesta.get_json() == []


# ---------- Rutas y métodos que no existen ----------


def test_ruta_inexistente_responde_404_en_json(client):
    # Arrange: ninguna
    # Act
    respuesta = client.get("/pajaros")
    # Assert
    assert respuesta.status_code == 404
    assert "error" in respuesta.get_json()


def test_metodo_no_permitido_responde_405_en_json(client):
    # Arrange: la ruta /avistamientos no acepta PATCH
    # Act
    respuesta = client.patch("/avistamientos")
    # Assert
    assert respuesta.status_code == 405
    assert "error" in respuesta.get_json()
    

    # ---------- Reloj real (sin stub) ----------


@pytest.fixture
def client_con_reloj_real(tmp_path):
    """Cliente que usa el reloj del sistema, el mismo que se usa en producción."""
    app = create_app({"DATABASE": str(tmp_path / "prueba.db"), "TESTING": True})
    return app.test_client()


def test_con_el_reloj_real_una_fecha_pasada_se_acepta(client_con_reloj_real):
    # Arrange: el año 2000 siempre es anterior a hoy
    datos = {**AVISTAMIENTO, "fecha": "2000-01-01"}
    # Act
    respuesta = client_con_reloj_real.post("/avistamientos", json=datos)
    # Assert
    assert respuesta.status_code == 201


def test_con_el_reloj_real_una_fecha_muy_futura_se_rechaza(client_con_reloj_real):
    # Arrange: el año 2999 siempre es posterior a hoy
    datos = {**AVISTAMIENTO, "fecha": "2999-01-01"}
    # Act
    respuesta = client_con_reloj_real.post("/avistamientos", json=datos)
    # Assert
    assert respuesta.status_code == 400
    assert set(respuesta.get_json()["campos"]) == {"fecha"}