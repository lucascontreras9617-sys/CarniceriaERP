from core.application.exceptions.venta_exceptions import VentaNoEncontradaError
from core.domain.value_objects.estado_venta import EstadoVenta
from core.application.use_cases.registrar_egreso_stock import RegistrarEgresoStock


class CerrarVenta:
    def __init__(
        self,
        venta_repository,
        stock_repository,
    ):
        self.venta_repository = venta_repository
        self.stock_repository = stock_repository
        self.registrar_egreso_stock = RegistrarEgresoStock(stock_repository)

    def ejecutar(self, venta_id: str) -> None:
        # 1️⃣ Obtener venta
        venta = self.venta_repository.obtener_por_id(venta_id)
        if venta is None:
            raise VentaNoEncontradaError()

        if venta.estado != EstadoVenta.ABIERTA:
            return  # idempotente

        # 2️⃣ Impactar stock (delegado)
        for item in venta.items:
            self.registrar_egreso_stock.ejecutar(
                producto_id=item.producto.id,
                cantidad=item.cantidad,
                referencia=f"VENTA:{venta.id}",
            )

        # 3️⃣ Cerrar venta
        venta.cerrar()

        # 4️⃣ Persistir
        self.venta_repository.guardar(venta)
