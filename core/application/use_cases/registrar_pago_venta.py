# core/application/use_cases/registrar_pago_venta.py

from datetime import date
from core.domain.entities.pago import Pago
from core.domain.value_objects.dinero import Dinero
from core.application.exceptions.venta_exceptions import VentaNoEncontradaError
from core.application.ports.venta_repository import VentaRepository

class RegistrarPagoVenta:
    def __init__(self, venta_repository: VentaRepository):
        self.venta_repository = venta_repository

    def ejecutar(
        self,
        venta_id: str,
        monto: Dinero,
        fecha: date | None = None
    ) -> None:
        venta = self.venta_repository.obtener_por_id(venta_id)
        if venta is None:
            raise VentaNoEncontradaError()

        if fecha is None:
            fecha = date.today()

        pago = Pago(monto, fecha)
        venta.registrar_pago(pago)
        self.venta_repository.guardar(venta)
