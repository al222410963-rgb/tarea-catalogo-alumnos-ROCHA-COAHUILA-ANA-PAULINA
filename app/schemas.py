"""Esquemas del Catálogo de Productos."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field  # noqa: F401  (ConfigDict: TODO 1)


class Categoria(str, Enum):
    perifericos = "perifericos"
    monitores = "monitores"
    almacenamiento = "almacenamiento"


class ProductoIn(BaseModel):
    sku: str = Field(pattern=r"^[A-Z]{3}-\d{3}$", examples=["TEC-001"])
    nombre: str = Field(min_length=3, max_length=80, examples=["Teclado mecánico"])
    precio: float = Field(gt=0, examples=[899.0])
    existencias: int = Field(ge=0, examples=[10])
    categoria: Categoria


class ProductoOut(ProductoIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    disponible: bool


class AjusteExistencias(BaseModel):
    cantidad: int = Field(examples=[5, -2])
