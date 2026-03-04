from dataclasses import dataclass
from datetime import datetime, date
from core.domain.value_objects.peso import Peso
from core.domain.value_objects.dinero import Dinero
from core.domain.exceptions import ValorInvalidoError


@dataclass
class InventoryLot:
    id: str
    producto_id: str
    cantidad_disponible: Peso
    costo_unitario: Dinero
    fecha_ingreso: datetime
    fecha_vencimiento: date | None

    def consumir(self, cantidad: Peso):
        if cantidad.valor <= 0:
            raise ValorInvalidoError("La cantidad a consumir debe ser positiva")

        if cantidad.valor > self.cantidad_disponible.valor:
            raise ValorInvalidoError("Cantidad supera el stock del lote")

        self.cantidad_disponible = Peso(
            self.cantidad_disponible.valor - cantidad.valor
        )

    def esta_vencido(self, hoy: date) -> bool:
        if self.fecha_vencimiento is None:
            return False
        return self.fecha_vencimiento < hoy

    def esta_disponible(self) -> bool:
        return self.cantidad_disponible.valor > 0
