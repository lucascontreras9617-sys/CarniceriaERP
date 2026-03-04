# core/application/port/venta_repository.py
from abc import ABC, abstractmethod
from typing import Optional
from core.domain.entities.venta import Venta

class VentaRepository(ABC):

    @abstractmethod
    def guardar(self, venta: Venta) -> None:
        pass

    @abstractmethod
    def obtener_por_id(self, venta_id: str) -> Venta:
        pass
