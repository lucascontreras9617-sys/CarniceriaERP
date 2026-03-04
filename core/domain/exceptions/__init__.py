"""
Excepciones específicas del dominio de negocio.
Cada excepción representa una regla de negocio violada.
"""

# ─────────────────────────────────────────────
# Base del dominio
# ─────────────────────────────────────────────

class DomainError(Exception):
    """Base para todas las excepciones del dominio"""
    pass


class ValorInvalidoError(DomainError):
    """Error cuando un valor no cumple con las reglas de negocio"""
    pass


# ─────────────────────────────────────────────
# Excepciones de stock / productos
# ─────────────────────────────────────────────

class StockInsuficienteError(DomainError):
    """Error cuando no hay stock suficiente para una operación"""
    pass


class ProductoInactivoError(DomainError):
    """Error al intentar operar con un producto inactivo"""
    pass


# ─────────────────────────────────────────────
# Excepciones de lotes
# ─────────────────────────────────────────────

from .lote_exceptions import LoteNoEncontradoError


__all__ = [
    "DomainError",
    "ValorInvalidoError",
    "StockInsuficienteError",
    "ProductoInactivoError",
    "LoteNoEncontradoError",
]
