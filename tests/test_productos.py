"""Las 16 pruebas de la Práctica 3, ahora sobre SQLite. NO modifiques este archivo.

La fixture `client` está en conftest.py.
"""

import pytest

TECLADO = {
    "sku": "TEC-001",
    "nombre": "Teclado mecánico",
    "precio": 899.0,
    "existencias": 10,
    "categoria": "perifericos",
}
MONITOR = {
    "sku": "MON-001",
    "nombre": "Monitor 24 pulgadas",
    "precio": 2999.0,
    "existencias": 0,
    "categoria": "monitores",
}


# --- Crear y validar -------------------------------------------------------


def test_01_crear_producto(client):
    r = client.post("/productos", json=TECLADO)
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 1
    assert body["sku"] == "TEC-001"
    assert body["disponible"] is True


def test_02_sin_existencias_no_esta_disponible(client):
    r = client.post("/productos", json=MONITOR)
    assert r.status_code == 201
    assert r.json()["disponible"] is False


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("sku", "tec-1"),  # formato incorrecto: debe ser AAA-000
        ("nombre", "TV"),  # menos de 3 caracteres
        ("precio", 0),  # debe ser mayor que 0
        ("existencias", -1),  # no puede ser negativo
        ("categoria", "comida"),  # no está en la lista
    ],
)
def test_03_datos_invalidos_devuelven_422(client, campo, valor):
    r = client.post("/productos", json={**TECLADO, campo: valor})
    assert r.status_code == 422


def test_04_sku_duplicado_devuelve_409(client):
    client.post("/productos", json=TECLADO)
    r = client.post("/productos", json={**TECLADO, "nombre": "Otro teclado"})
    assert r.status_code == 409
    assert r.json()["detail"] == "El SKU ya existe"


# --- Leer ------------------------------------------------------------------


def test_05_obtener_inexistente_devuelve_404(client):
    r = client.get("/productos/99")
    assert r.status_code == 404
    assert r.json()["detail"] == "Producto no encontrado"


def test_06_listar_con_filtros(client):
    client.post("/productos", json=TECLADO)
    client.post("/productos", json=MONITOR)
    assert len(client.get("/productos").json()) == 2
    monitores = client.get("/productos", params={"categoria": "monitores"}).json()
    assert [p["sku"] for p in monitores] == ["MON-001"]
    disponibles = client.get("/productos", params={"solo_disponibles": True}).json()
    assert [p["sku"] for p in disponibles] == ["TEC-001"]


# --- Actualizar y eliminar -------------------------------------------------


def test_07_actualizar_recalcula_disponible(client):
    client.post("/productos", json=TECLADO)
    r = client.put("/productos/1", json={**TECLADO, "existencias": 0})
    assert r.status_code == 200
    assert r.json()["disponible"] is False


def test_08_actualizar_inexistente_devuelve_404(client):
    r = client.put("/productos/99", json=TECLADO)
    assert r.status_code == 404


def test_09_eliminar(client):
    client.post("/productos", json=TECLADO)
    assert client.delete("/productos/1").status_code == 204
    assert client.get("/productos/1").status_code == 404


# --- Ajustar existencias ---------------------------------------------------


def test_10_ajustar_existencias(client):
    client.post("/productos", json=TECLADO)
    r = client.patch("/productos/1/existencias", json={"cantidad": 5})
    assert r.status_code == 200
    assert r.json()["existencias"] == 15
    r = client.patch("/productos/1/existencias", json={"cantidad": -15})
    assert r.json()["existencias"] == 0
    assert r.json()["disponible"] is False


def test_11_no_permite_existencias_negativas(client):
    client.post("/productos", json=TECLADO)
    r = client.patch("/productos/1/existencias", json={"cantidad": -11})
    assert r.status_code == 409
    assert r.json()["detail"] == "Existencias insuficientes"
    assert client.get("/productos/1").json()["existencias"] == 10


def test_12_ajustar_inexistente_devuelve_404(client):
    r = client.patch("/productos/99/existencias", json={"cantidad": 1})
    assert r.status_code == 404
