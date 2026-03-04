# app/dominio/value_objects/cantidad.py
from ..exceptions import ValorInvalidoError
from .dinero import Dinero


class Cantidad:
    """
    Value Object para cantidades físicas (kg, unidades).
    Asegura valores positivos y unidad coherente.
    """

    UNIDADES_VALIDAS = {'kg', 'unidades', 'litros', 'gramos'}

    def __init__(self, valor, unidad='kg'):
        if valor < 0:
            raise ValorInvalidoError("La cantidad no puede ser negativa")

        if unidad not in self.UNIDADES_VALIDAS:
            raise ValorInvalidoError(f"Unidad '{unidad}' no válida")

        self._valor = float(valor)
        self._unidad = unidad

    @property
    def valor(self):
        return self._valor

    @property
    def unidad(self):
        return self._unidad

    def __add__(self, other):
        if not isinstance(other, Cantidad):
            raise TypeError("Solo se puede sumar Cantidad con Cantidad")

        if self.unidad != other.unidad:
            raise ValorInvalidoError(
                f"No se pueden sumar {self.unidad} con {other.unidad}"
            )

        return Cantidad(self.valor + other.valor, self.unidad)

    def __sub__(self, other):
        if not isinstance(other, Cantidad):
            raise TypeError("Solo se puede restar Cantidad con Cantidad")

        if self.unidad != other.unidad:
            raise ValorInvalidoError(
                f"No se pueden restar {self.unidad} con {other.unidad}"
            )

        resultado = self.valor - other.valor
        if resultado < 0:
            raise ValorInvalidoError("No puede haber cantidad negativa")

        return Cantidad(resultado, self.unidad)

    def __mul__(self, other):
        """Cantidad × escalar o Cantidad × Dinero"""

        if isinstance(other, (int, float)):
            return Cantidad(self.valor * other, self.unidad)

        if isinstance(other, Dinero):
            return Dinero(self.valor * other.monto, other.moneda)

        raise TypeError("Solo se puede multiplicar por número o Dinero")

    def __truediv__(self, divisor):
        if not isinstance(divisor, (int, float)):
            raise TypeError("Solo se puede dividir por número")

        if divisor <= 0:
            raise ValorInvalidoError("El divisor debe ser positivo")

        return Cantidad(self.valor / divisor, self.unidad)

    def __eq__(self, other):
        if not isinstance(other, Cantidad):
            return False

        return self.valor == other.valor and self.unidad == other.unidad

    def __lt__(self, other):
        if not isinstance(other, Cantidad):
            raise TypeError("Solo se puede comparar Cantidad con Cantidad")

        if self.unidad != other.unidad:
            raise ValorInvalidoError("Unidades diferentes no comparables")

        return self.valor < other.valor

    def __str__(self):
        return f"{self.valor:.3f} {self.unidad}"

    def __repr__(self):
        return f"Cantidad(valor={self.valor}, unidad='{self.unidad}')"

    def es_mayor_que(self, cantidad):
        if not isinstance(cantidad, Cantidad):
            raise TypeError("Solo se puede comparar con Cantidad")

        if self.unidad != cantidad.unidad:
            raise ValorInvalidoError("Unidades diferentes no comparables")

        return self.valor > cantidad.valor

    @classmethod
    def zero(cls, unidad='kg'):
        return cls(0.0, unidad)
