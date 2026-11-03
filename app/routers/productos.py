"""Router del Catálogo de Productos."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..repository import ExistenciasInsuficientes, SkuDuplicado
from ..repository_sql import SqlProductoRepository, get_repo
from ..schemas import AjusteExistencias, Categoria, ProductoIn, ProductoOut

router = APIRouter(prefix="/productos", tags=["Productos"])

Repo = Annotated[SqlProductoRepository, Depends(get_repo)]

NO_ENCONTRADO = "Producto no encontrado"


@router.post("", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(data: ProductoIn, repo: Repo) -> ProductoOut:
    try:
        return repo.add(data)
    except SkuDuplicado:
        raise HTTPException(status_code=409, detail="El SKU ya existe") from None


@router.get("", response_model=list[ProductoOut])
def listar_productos(
    repo: Repo, categoria: Categoria | None = None, solo_disponibles: bool = False
) -> list[ProductoOut]:
    return repo.list(categoria, solo_disponibles)


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(producto_id: int, repo: Repo) -> ProductoOut:
    producto = repo.get(producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail=NO_ENCONTRADO)
    return producto


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(producto_id: int, data: ProductoIn, repo: Repo) -> ProductoOut:
    try:
        producto = repo.update(producto_id, data)
    except SkuDuplicado:
        raise HTTPException(status_code=409, detail="El SKU ya existe") from None
    if producto is None:
        raise HTTPException(status_code=404, detail=NO_ENCONTRADO)
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int, repo: Repo) -> Response:
    if not repo.delete(producto_id):
        raise HTTPException(status_code=404, detail=NO_ENCONTRADO)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{producto_id}/existencias", response_model=ProductoOut)
def ajustar_existencias(producto_id: int, ajuste: AjusteExistencias, repo: Repo) -> ProductoOut:
    try:
        producto = repo.ajustar_existencias(producto_id, ajuste.cantidad)
    except ExistenciasInsuficientes:
        raise HTTPException(status_code=409, detail="Existencias insuficientes") from None
    if producto is None:
        raise HTTPException(status_code=404, detail=NO_ENCONTRADO)
    return producto
