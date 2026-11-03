"""Especificación de la página del catálogo. NO modifiques este archivo."""

FORMULARIO = {
    "sku": "TEC-001",
    "nombre": "Teclado mecánico",
    "precio": "899",
    "existencias": "10",
    "categoria": "perifericos",
}


def test_w1_pagina_vacia(client):
    r = client.get("/web/productos")
    assert r.status_code == 200
    assert "El catálogo está vacío" in r.text
    assert 'name="sku"' in r.text


def test_w2_formulario_valido_guarda_y_redirige(client):
    r = client.post("/web/productos", data=FORMULARIO, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/web/productos"
    assert client.get("/productos/1").json()["nombre"] == "Teclado mecánico"


def test_w3_lista_muestra_productos(client):
    client.post("/web/productos", data=FORMULARIO)
    r = client.get("/web/productos")
    assert "TEC-001" in r.text
    assert "$899.00" in r.text


def test_w4_formulario_invalido_muestra_errores(client):
    r = client.post("/web/productos", data={**FORMULARIO, "sku": "tec-1"})
    assert r.status_code == 422
    assert "String should match pattern" in r.text
    assert client.get("/productos").json() == []


def test_w5_sku_repetido_muestra_aviso(client):
    client.post("/web/productos", data=FORMULARIO)
    r = client.post("/web/productos", data={**FORMULARIO, "nombre": "Otro teclado"})
    assert r.status_code == 409
    assert "El SKU ya existe" in r.text
    assert len(client.get("/productos").json()) == 1
