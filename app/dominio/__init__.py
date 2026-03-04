# app/dominio/__init__.py
"""
Módulo de dominio del sistema Carnicería ERP.
Contiene las entidades de negocio, value objects y reglas de negocio.
"""

from .exceptions import *
from .value_objects.dinero import Dinero
from .value_objects.cantidad import Cantidad
from .entities.producto import Producto
from .entities.venta_item import VentaItem
from .entities.venta import Venta

__all__ = [
    # Exceptions
    'DomainError',
    'ValorInvalidoError',
    'StockInsuficienteError',
    'VentaCerradaError',
    'VentaSinItemsError',
    'LimiteCreditoExcedidoError',
    'ProductoInactivoError',
    
    # Value Objects
    'Dinero',
    'Cantidad',
    
    # Entities
    'Producto',
    'VentaItem',
    'Venta'
]