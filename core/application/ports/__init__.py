"""
Ports/Interfaces de la aplicación
"""
from .venta_repository import VentaRepository
from .producto_repository import ProductoRepository
from .lote_repository import LoteRepository
from .lote_repository import LoteRepository as LoteRepo
from .producto_repository import ProductoRepository as ProductoRepo

__all__ = [
    'VentaRepository',
    'LoteRepository',
    'ProductoRepository',
    'LoteRepo',
    'ProductoRepo'
]
