# tests/application/fakes/fake_venta_repository.py

from datetime import date
from core.application.ports.venta_repository import VentaRepository

class FakeVentaRepository(VentaRepository):
    def __init__(self):
        self.ventas = {}
        self.guardadas = []

    # === Métodos usados por el caso de uso ===

    def obtener_por_id(self, venta_id: str):
        return self.ventas.get(venta_id)

    def guardar(self, venta):
        self.ventas[venta.id] = venta
        self.guardadas.append(venta)

    # === Métodos requeridos por la interfaz (aunque no se usen acá) ===

    def obtener_todas(self):
        return list(self.ventas.values())

    def obtener_por_fecha(self, fecha: date):
        # Fake simple: no filtra, solo devuelve todas
        return list(self.ventas.values())

