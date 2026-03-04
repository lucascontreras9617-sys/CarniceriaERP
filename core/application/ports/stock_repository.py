from abc import ABC, abstractmethod
from core.domain.entities.stock import Stock


class StockRepository(ABC):

    @abstractmethod
    def obtener_por_producto(self, producto_id: str) -> Stock:
        pass

    @abstractmethod
    def guardar(self, stock: Stock) -> None:
        pass
