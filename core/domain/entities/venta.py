from datetime import date
from typing import List, Optional
from uuid import uuid4

from core.domain.entities.pago import Pago
from core.domain.entities.cliente import Cliente
from core.domain.value_objects.dinero import Dinero
from core.domain.value_objects.tipo_pago import TipoPago
from core.domain.value_objects.presentacion import Presentacion
from core.domain.value_objects.estado_venta import EstadoVenta
from core.domain.value_objects import Cantidad
from core.domain.exceptions.venta_exceptions import (
    VentaCerradaError,
    VentaSinItemsError,
    VentaFueraDePlazoError,
    VentaNoCancelableError,
)


class VentaItem:
    def __init__(self, producto, cantidad, precio_unitario, presentacion):
        presentacion.validar_cantidad(cantidad)

        self.producto = producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.presentacion = presentacion

        self.subtotal = precio_unitario * cantidad.valor


class Venta:
    def __init__(
        self,
        tipo_pago: TipoPago = TipoPago.EFECTIVO,
        cliente: Optional[Cliente] = None,
        fecha: Optional[date] = None,
        id: Optional[str] = None,
    ):
        self.id = id or str(uuid4())

        if tipo_pago.es_a_credito() and cliente is None:
            raise ValueError("Una venta a crédito requiere un cliente")

        self.tipo_pago = tipo_pago
        self.cliente = cliente
        self.fecha = fecha or date.today()

        self.estado = EstadoVenta.ABIERTA
        self.items: List[VentaItem] = []

        self.total: Dinero = Dinero(0)
        self.deuda_generada: Dinero = Dinero(0)
        self.pagos: List[Pago] = []

    # -------------------------
    # ITEMS
    # -------------------------

    def agregar_item(
        self,
        producto,
        cantidad: Cantidad,
        precio_unitario: Dinero,
        presentacion: Presentacion,
    ) -> None:
        if self.estado != EstadoVenta.ABIERTA:
            raise VentaCerradaError()

        item = VentaItem(
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            presentacion=presentacion,
        )

        self.items.append(item)
        self.total = self.total + item.subtotal

    # -------------------------
    # CIERRE
    # -------------------------

    def cerrar(self) -> None:
        if self.estado != EstadoVenta.ABIERTA:
            raise VentaCerradaError()

        if not self.items:
            raise VentaSinItemsError()

        if self.tipo_pago.es_a_credito():
            self.cliente.validar_compra_a_credito(self.total)
            self.cliente.registrar_deuda(self.total)
            self.deuda_generada = self.total

        for item in self.items:
            item.producto.reducir_stock(
                item.cantidad,
                item.presentacion,
            )

        self.estado = EstadoVenta.CERRADA
