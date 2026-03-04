from datetime import date


class Pago:
    def __init__(self, monto: float, fecha: date):
        self.monto = monto
        self.fecha = fecha
