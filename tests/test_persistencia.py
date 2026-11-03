"""Especificación del repositorio SQL. NO modifiques este archivo."""

import pytest

from app.repository import SkuDuplicado
from app.repository_sql import SqlProductoRepository
from app.schemas import ProductoIn

TECLADO = ProductoIn(
    sku="TEC-001", nombre="Teclado mecánico", precio=899.0, existencias=10, categoria="perifericos"
)


def test_p1_los_datos_sobreviven_a_la_sesion(sesiones):
    with sesiones() as session:
        creado = SqlProductoRepository(session).add(TECLADO)
    with sesiones() as otra_session:
        leido = SqlProductoRepository(otra_session).get(creado.id)
    assert leido is not None
    assert leido.existencias == 10


def test_p2_la_bd_rechaza_sku_duplicado_y_la_sesion_sigue_usable(sesiones):
    with sesiones() as session:
        repo = SqlProductoRepository(session)
        repo.add(TECLADO)
        with pytest.raises(SkuDuplicado):
            repo.add(TECLADO)
        # tras el rollback, la sesión debe seguir funcionando
        assert len(repo.list()) == 1
