# core/application/port/producto_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
from core.domain.entities.producto import Producto

class ProductoRepository(ABC):

    @abstractmethod
    def guardar(self, producto: Producto) -> None:
        pass

    @abstractmethod
    def obtener_por_id(self, producto_id: str) -> Producto:
        pass

    @abstractmethod
    def obtener_todos(self) -> List[Producto]:
        pass


