"""
Dinero - Value Object para montos monetarios
"""
"""
Dinero - Value Object para montos monetarios
"""
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from typing import Union, Self
from core.domain.value_objects.cantidad import Cantidad


@dataclass(frozen=True)
class Dinero:
    """Value Object inmutable para montos monetarios"""
    monto: Decimal
    moneda: str = "ARS"

    # -------------------------
    # Inicialización
    # -------------------------

    def __post_init__(self):
        if not isinstance(self.monto, Decimal):
            object.__setattr__(
                self, "monto", Decimal(str(self.monto))
            )

        if self.monto < Decimal("0"):
            raise ValueError(
                "El monto no puede ser negativo"
            )

        object.__setattr__(
            self,
            "monto",
            self.monto.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            ),
        )

    # -------------------------
    # Fábricas
    # -------------------------

    @classmethod
    def desde_monto(
        cls, monto: Union[int, float, str]
    ) -> Self:
        return cls(Decimal(str(monto)))

    @classmethod
    def cero(cls) -> Self:
        return cls(Decimal("0"))

    # -------------------------
    # Validaciones internas
    # -------------------------

    def _validar_operacion(self, other: Self):
        if not isinstance(other, Dinero):
            raise TypeError(
                "La operación requiere otro Dinero"
            )
        if self.moneda != other.moneda:
            raise ValueError(
                "Monedas incompatibles"
            )

    # -------------------------
    # Comparaciones
    # -------------------------

    def __eq__(self, other: Self) -> bool:
        self._validar_operacion(other)
        return self.monto == other.monto

    def __lt__(self, other: Self) -> bool:
        self._validar_operacion(other)
        return self.monto < other.monto

    def __le__(self, other: Self) -> bool:
        self._validar_operacion(other)
        return self.monto <= other.monto

    def __gt__(self, other: Self) -> bool:
        self._validar_operacion(other)
        return self.monto > other.monto

    def __ge__(self, other: Self) -> bool:
        self._validar_operacion(other)
        return self.monto >= other.monto

    # -------------------------
    # Operaciones aritméticas
    # -------------------------

    def __add__(self, other: Self) -> Self:
        self._validar_operacion(other)
        return Dinero(
            self.monto + other.monto,
            self.moneda,
        )

    def __sub__(self, other: Self) -> Self:
        self._validar_operacion(other)
        resultado = self.monto - other.monto

        if resultado < Decimal("0"):
            resultado = Decimal("0")

        return Dinero(resultado, self.moneda)

    def __mul__(
        self, factor: Union[int, float, Decimal, "Cantidad"]
    ) -> Self:
     from core.domain.value_objects.cantidad import Cantidad

     if isinstance(factor, Cantidad):
        return Dinero(
            self.monto * factor.valor,
            self.moneda,
        )

     if isinstance(factor, (int, float)):
        factor = Decimal(str(factor))

     if not isinstance(factor, Decimal):
        raise TypeError(
            "Dinero solo puede multiplicarse por número o Cantidad"
        )

     return Dinero(
        self.monto * factor,
        self.moneda,
    )


    def __truediv__(
        self, divisor: Union[int, float, Decimal]
    ) -> Self:
        if isinstance(divisor, (int, float)):
            divisor = Decimal(str(divisor))

        if divisor == Decimal("0"):
            raise ValueError(
                "División por cero"
            )

        return Dinero(
            self.monto / divisor,
            self.moneda,
        )

    # -------------------------
    # Representación
    # -------------------------

    def __str__(self) -> str:
        return f"${self.monto:,.2f} {self.moneda}"

    def __repr__(self) -> str:
        return f"Dinero({self.monto} {self.moneda})"
