from .base import DomainException

class ProductoException(DomainException):
    pass

class StockInsuficienteError(ProductoException):
    def __init__(self, producto, disponible, solicitado):
        super().__init__(
            f"Stock insuficiente para {producto}. "
            f"Disponible: {disponible}, solicitado: {solicitado}"
        )

class CantidadInvalidaError(ProductoException):
    pass

class PresentacionNoDisponibleError(ProductoException):
    pass
