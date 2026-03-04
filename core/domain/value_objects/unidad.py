from decimal import Decimal
from core.domain.value_objects.cantidad import Cantidad
from core.domain.exceptions import ValorInvalidoError


class Unidad(Cantidad):
    UNIDAD = "unidades"

    def __init__(self, valor):
        try:
            valor = int(valor)
        except Exception:
            raise ValorInvalidoError("La cantidad de unidades debe ser entera")

        if valor <= 0:
            raise ValorInvalidoError("Las unidades deben ser mayores a cero")

        super().__init__(Decimal(valor))

    def __add__(self, other):
        if not isinstance(other, Unidad):
            raise TypeError("Solo se puede sumar Unidad con Unidad")
        return Unidad(int(self.valor + other.valor))

    def __sub__(self, other):
        if not isinstance(other, Unidad):
            raise TypeError("Solo se puede restar Unidad con Unidad")

        resultado = self.valor - other.valor
        if resultado < 0:
            raise ValorInvalidoError("No puede haber unidades negativas")

        return Unidad(int(resultado))

    def __eq__(self, other):
        return isinstance(other, Unidad) and self.valor == other.valor

    def __str__(self):
        return f"{int(self.valor)} unidades"

    def __repr__(self):
        return f"Unidad({int(self.valor)})"
