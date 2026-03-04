from dataclasses import dataclass
from core.domain.value_objects.peso import Peso
from core.domain.value_objects.dinero import Dinero


@dataclass(frozen=True)
class ConsumoLote:
    lote_id: str
    cantidad: Peso
    costo_unitario: Dinero

    @property
    def costo_total(self) -> Dinero:
        return self.costo_unitario * self.cantidad.valor
