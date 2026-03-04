from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from typing import Union
from core.domain.exceptions import ValorInvalidoError

@dataclass(frozen=True)
class Peso:
    """
    Value Object para pesos en kilogramos.
    Ej: 1.250 kg de carne
    """
    valor: Decimal
    unidad: str = "kg"

    def __post_init__(self):
        if not isinstance(self.valor, Decimal):
            object.__setattr__(self, "valor", Decimal(str(self.valor)))

        if self.valor < Decimal("0"):
         raise ValorInvalidoError("El peso no puede ser negativo")

        object.__setattr__(
            self,
            "valor",
            self.valor.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
        )

    @classmethod
    def desde_kg(cls, kg: Union[int, float, str]) -> "Peso":
        return cls(Decimal(str(kg)))

    @property
    def en_kg(self) -> float:
        return float(self.valor)

    def __str__(self):
        return f"{self.valor} kg"

    def __repr__(self):
        return f"Peso({self.valor} kg)"
