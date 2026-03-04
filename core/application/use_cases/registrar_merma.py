from core.domain.exceptions.stock_exceptions import StockNoEncontradoError
from core.domain.value_objects.peso import Peso


class RegistrarMerma:
    def __init__(self, stock_repository):
        self.stock_repository = stock_repository

    def ejecutar(self, producto_id: str, cantidad: Peso, motivo: str) -> None:
        stock = self.stock_repository.obtener_por_producto(producto_id)

        if stock is None:
            raise StockNoEncontradoError()

        stock.registrar_merma(
            cantidad=cantidad,
            motivo=motivo
        )

        self.stock_repository.guardar(stock)
