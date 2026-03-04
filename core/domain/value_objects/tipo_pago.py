from enum import Enum

class TipoPago(Enum):
    EFECTIVO = "EFECTIVO"
    DEBITO = "DEBITO"
    CREDITO = "CREDITO"

    def es_a_credito(self) -> bool:
        return self == TipoPago.CREDITO
