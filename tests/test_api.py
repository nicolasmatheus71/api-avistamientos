import pytest

from app import create_app

AVISTAMIENTO = {
    "especie": "colibrí",
    "lugar": "Bogotá",
    "fecha": "2026-10-04",
    "observador": "Laura",
}


@pytest.fixture
def client(tmp_path):
    """Cliente de pruebas con una base de datos temporal y vacía."""
    app = create_app({"DATABASE": str(tmp_path / "prueba.db"), "TESTING": True})
    return app.test_client()


def crear(client, **cambios):
    return client.post("/avistamientos", json={**AVISTAMIENTO, **cambios})


def test_listar_vacio(client):
    respuesta = client.get("/avistamientos")
    assert respuesta.status_code == 200
    assert respuesta.get_json() == []


def test_registrar_devuelve_201(client):
    respuesta = crear(client)
    assert respuesta.status_code == 201
    datos = respuesta.get_json()
    assert datos["id"] == 1
    assert datos["especie"] == "colibrí"
    assert datos["observador"] == "Laura"


def test_registrar_sin_datos_devuelve_400(client):
    respuesta = client.post("/avistamientos", json={"especie": "colibrí"})
    assert respuesta.status_code == 400
    assert "error" in respuesta.get_json()


@pytest.mark.parametrize("fecha", ["04/10/2026", "2026-13-45"])
def test_registrar_con_fecha_invalida_devuelve_400(client, fecha):
    respuesta = crear(client, fecha=fecha)
    assert respuesta.status_code == 400


def test_registrar_sin_json_devuelve_400(client):
    respuesta = client.post(
        "/avistamientos", data="esto no es json", content_type="application/json"
    )
    assert respuesta.status_code == 400


def test_listar_con_datos(client):
    crear(client)
    crear(client, especie="águila")
    respuesta = client.get("/avistamientos")
    assert respuesta.status_code == 200
    assert len(respuesta.get_json()) == 2


def test_ver_existente_devuelve_200(client):
    crear(client)
    respuesta = client.get("/avistamientos/1")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["lugar"] == "Bogotá"


def test_ver_inexistente_devuelve_404(client):
    respuesta = client.get("/avistamientos/999")
    assert respuesta.status_code == 404


def test_actualizar_devuelve_200(client):
    crear(client)
    cambios = {**AVISTAMIENTO, "especie": "águila"}
    respuesta = client.put("/avistamientos/1", json=cambios)
    assert respuesta.status_code == 200
    assert respuesta.get_json()["especie"] == "águila"
    assert client.get("/avistamientos/1").get_json()["especie"] == "águila"


def test_actualizar_inexistente_devuelve_404(client):
    respuesta = client.put("/avistamientos/999", json=AVISTAMIENTO)
    assert respuesta.status_code == 404


def test_actualizar_incompleto_devuelve_400(client):
    crear(client)
    respuesta = client.put("/avistamientos/1", json={"especie": "águila"})
    assert respuesta.status_code == 400


def test_eliminar_devuelve_204(client):
    crear(client)
    respuesta = client.delete("/avistamientos/1")
    assert respuesta.status_code == 204
    assert respuesta.data == b""
    assert client.get("/avistamientos/1").status_code == 404


def test_eliminar_inexistente_devuelve_404(client):
    respuesta = client.delete("/avistamientos/999")
    assert respuesta.status_code == 404


def test_resumen_por_especie(client):
    crear(client)
    crear(client)
    crear(client, especie="águila")
    respuesta = client.get("/avistamientos/resumen")
    assert respuesta.status_code == 200
    assert respuesta.get_json() == [
        {"cantidad": 2, "especie": "colibrí"},
        {"cantidad": 1, "especie": "águila"},
    ]