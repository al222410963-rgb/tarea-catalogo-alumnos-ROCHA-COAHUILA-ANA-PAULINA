"""Conexión a la base de datos con SQLAlchemy."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

URL_BD = "sqlite:///./catalogo.db"

engine = create_engine(URL_BD, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Clase base de todos los modelos (tablas)."""


def get_session() -> Iterator[Session]:
    """Dependencia: abre una sesión por petición y la cierra al terminar."""
    with SessionLocal() as session:
        yield session
