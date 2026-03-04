from core.application.ports.stock_repository import StockRepository
from core.domain.entities.stock import Stock
from core.domain.exceptions.stock_exceptions import StockNoEncontradoError


class FakeStockRepository(StockRepository):

    def __init__(self):
        self._stocks = {}

    def agregar(self, stock: Stock):
        self._stocks[stock.producto_id] = stock

    def obtener_por_producto(self, producto_id: str) -> Stock:
        if producto_id not in self._stocks:
            raise StockNoEncontradoError(
                f"No existe stock para producto {producto_id}"
            )
        return self._stocks[producto_id]

    def guardar(self, stock: Stock) -> None:
        self._stocks[stock.producto_id] = stock
