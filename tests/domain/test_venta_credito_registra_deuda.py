import pytest

from core.domain.entities.cliente import ClienteCrediticio
from core.domain.entities.producto import Producto
from core.domain.entities.venta import Venta
from core.domain.value_objects.tipo_pago import TipoPago
from core.domain.value_objects.presentacion import TipoPresentacion
from core.domain.value_objects.estado_venta import EstadoVenta
from core.domain.value_objects.presentacion import Presentacion


def test_venta_a_credito_registra_deuda_en_el_cliente():
    producto = Producto(
        "P1",
        "Bife",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )
    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 10.0

    cliente = ClienteCrediticio(
        id="C1",
        nombre="Juan Perez",
        documento="20-12345678-9",
        limite_credito=2000,
        saldo_deudor=500
    )

    venta = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente
    )

    venta.agregar_item(
        producto,
        1.0,
        TipoPresentacion.POR_PESO,
        1000
    )

    venta.cerrar()

    assert cliente.saldo_deudor == 1500
    assert venta.estado == EstadoVenta.CERRADA
