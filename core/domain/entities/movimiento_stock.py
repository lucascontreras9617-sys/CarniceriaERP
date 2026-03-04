from dataclasses import dataclass
from datetime import datetime
from core.domain.value_objects.peso import Peso
from core.domain.value_objects.dinero import Dinero


@dataclass(frozen=True)
class MovimientoStock:
    tipo: str  # INGRESO | EGRESO | MERMA
    cantidad: Peso
    referencia: str
    costo_unitario: Dinero | None
    fecha: datetime

    @staticmethod
    def ingreso(cantidad: Peso, costo_unitario: Dinero, referencia: str):
        return MovimientoStock(
            tipo="INGRESO",
            cantidad=cantidad,
            referencia=referencia,
            costo_unitario=costo_unitario,
            fecha=datetime.utcnow()
        )

    @staticmethod
    def egreso(cantidad: Peso, referencia: str):
        return MovimientoStock(
            tipo="EGRESO",
            cantidad=cantidad,
            referencia=referencia,
            costo_unitario=None,
            fecha=datetime.utcnow()
        )

    @staticmethod
    def merma(cantidad: Peso, motivo: str):
        return MovimientoStock(
            tipo="MERMA",
            cantidad=cantidad,
            referencia=motivo,
            costo_unitario=None,
            fecha=datetime.utcnow()
        )
