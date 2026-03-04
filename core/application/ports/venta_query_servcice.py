# core/application/port/venta_query_service.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

class VentaQueryService(ABC):

    @abstractmethod
    def obtener_por_fecha(self, desde: datetime, hasta: datetime) -> List[dict]:
        pass
