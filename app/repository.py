"""Repositorio en memoria del Catálogo de Productos."""

from .schemas import Categoria, ProductoIn, ProductoOut


class SkuDuplicado(Exception):
    """Ya existe otro producto con ese SKU."""


class ExistenciasInsuficientes(Exception):
    """El ajuste dejaría las existencias en negativo."""


class ProductoRepository:
    def __init__(self) -> None:
        self._items: dict[int, ProductoOut] = {}
        self._next_id = 1

    def _sku_en_uso(self, sku: str, excepto_id: int | None = None) -> bool:
        return any(p.sku == sku and p.id != excepto_id for p in self._items.values())

    def add(self, data: ProductoIn) -> ProductoOut:
        if self._sku_en_uso(data.sku):
            raise SkuDuplicado(data.sku)
        producto = ProductoOut(
            **data.model_dump(), id=self._next_id, disponible=data.existencias > 0
        )
        self._items[producto.id] = producto
        self._next_id += 1
        return producto

    def list(
        self, categoria: Categoria | None = None, solo_disponibles: bool = False
    ) -> list[ProductoOut]:
        productos = list(self._items.values())
        if categoria is not None:
            productos = [p for p in productos if p.categoria == categoria]
        if solo_disponibles:
            productos = [p for p in productos if p.disponible]
        return productos

    def get(self, producto_id: int) -> ProductoOut | None:
        return self._items.get(producto_id)

    def update(self, producto_id: int, data: ProductoIn) -> ProductoOut | None:
        if producto_id not in self._items:
            return None
        if self._sku_en_uso(data.sku, excepto_id=producto_id):
            raise SkuDuplicado(data.sku)
        producto = ProductoOut(**data.model_dump(), id=producto_id, disponible=data.existencias > 0)
        self._items[producto_id] = producto
        return producto

    def delete(self, producto_id: int) -> bool:
        return self._items.pop(producto_id, None) is not None

    def ajustar_existencias(self, producto_id: int, cantidad: int) -> ProductoOut | None:
        actual = self._items.get(producto_id)
        if actual is None:
            return None
        nuevas = actual.existencias + cantidad
        if nuevas < 0:
            raise ExistenciasInsuficientes(nuevas)
        producto = actual.model_copy(update={"existencias": nuevas, "disponible": nuevas > 0})
        self._items[producto_id] = producto
        return producto


repo = ProductoRepository()


def get_repo() -> ProductoRepository:
    return repo
