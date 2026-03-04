from enum import Enum
from core.domain.exceptions.producto_exceptions import CantidadInvalidaError
from core.domain.value_objects.peso import Peso
from core.domain.value_objects.cantidad import Cantidad


class TipoPresentacion(Enum):
    POR_PESO = "POR_PESO"
    POR_UNIDAD = "POR_UNIDAD"


class Presentacion:
    def __init__(self, tipo: TipoPresentacion):
        self.tipo = tipo

    def validar_cantidad(self, cantidad) -> None:
        if self.tipo == TipoPresentacion.POR_PESO:
            if not isinstance(cantidad, Peso):
                raise CantidadInvalidaError(
                    "Para presentación POR_PESO se requiere un Peso"
                )

        elif self.tipo == TipoPresentacion.POR_UNIDAD:
            if not isinstance(cantidad, Cantidad):
                raise CantidadInvalidaError(
                    "Para presentación POR_UNIDAD se requiere Cantidad"
                )
