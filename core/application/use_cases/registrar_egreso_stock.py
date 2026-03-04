from core.domain.exceptions.stock_exceptions import (
    StockNoEncontradoError,
    StockInsuficienteError,
)
from core.domain.entities.stock import Stock
from core.domain.value_objects.peso import Peso


class RegistrarEgresoStock:
    def __init__(self, stock_repository):
        self.stock_repository = stock_repository

    def ejecutar(self, producto_id: str, cantidad: Peso, referencia: str) -> None:
        stock = self.stock_repository.obtener_por_producto(producto_id)

        if stock is None:
            raise StockNoEncontradoError()

        try:
            stock.egresar(
                cantidad=cantidad,
                referencia=referencia,
            )
        except Exception as e:
            # solo dejamos pasar errores de dominio
            raise

        self.stock_repository.guardar(stock)
