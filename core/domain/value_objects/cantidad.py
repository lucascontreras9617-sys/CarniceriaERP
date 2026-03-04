from ..exceptions import ValorInvalidoError


class Cantidad:
    """
    Value Object para cantidades DISCRETAS (unidades).
    Ej: 1 pollo, 2 chorizos, 6 empanadas
    """

    def __init__(self, valor: int):
        if not isinstance(valor, int):
            raise ValorInvalidoError("La cantidad debe ser un número entero")

        if valor <= 0:
            raise ValorInvalidoError("La cantidad debe ser mayor a cero")

        self._valor = valor

    @property
    def valor(self) -> int:
        return self._valor

    def __add__(self, other):
        if not isinstance(other, Cantidad):
            raise TypeError("Solo se puede sumar Cantidad con Cantidad")
        return Cantidad(self.valor + other.valor)

    def __sub__(self, other):
        if not isinstance(other, Cantidad):
            raise TypeError("Solo se puede restar Cantidad con Cantidad")

        resultado = self.valor - other.valor
        if resultado <= 0:
            raise ValorInvalidoError("La cantidad resultante debe ser mayor a cero")

        return Cantidad(resultado)

    def __eq__(self, other):
        return isinstance(other, Cantidad) and self.valor == other.valor

    def __str__(self):
        return f"{self.valor} unidades"

    def __repr__(self):
        return f"Cantidad({self.valor})"
