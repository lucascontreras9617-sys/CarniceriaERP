# app/dominio/exceptions/__init__.py
"""
Excepciones específicas del dominio de negocio.
Cada excepción representa una regla de negocio violada.
"""

class DomainError(Exception):
    """Base para todas las excepciones del dominio"""
    pass

class ValorInvalidoError(DomainError):
    """Error cuando un valor no cumple con las reglas de negocio"""
    pass

class StockInsuficienteError(DomainError):
    """Error cuando no hay stock suficiente para una operación"""
    pass

class VentaCerradaError(DomainError):
    """Error al intentar modificar una venta cerrada"""
    pass

class VentaSinItemsError(DomainError):
    """Error al intentar cerrar una venta sin items"""
    pass

class LimiteCreditoExcedidoError(DomainError):
    """Error cuando un cliente excede su límite de crédito"""
    pass

class ProductoInactivoError(DomainError):
    """Error al intentar operar con producto inactivo"""
    pass

# NO es necesario el __all__ si defines las clases directamente en el __init__.py
# Python las exportará automáticamente