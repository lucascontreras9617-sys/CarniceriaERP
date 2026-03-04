import pytest

from core.domain.entities.venta import Venta
from core.domain.entities.producto import Producto
from core.domain.entities.cliente import ClienteCrediticio
from core.domain.value_objects.tipo_pago import TipoPago
from core.domain.value_objects.presentacion import TipoPresentacion
from core.domain.value_objects.presentacion import Presentacion


def test_cancelar_venta_a_credito_revierte_deuda():
    cliente = ClienteCrediticio(
        id="C1",
        nombre="Juan Perez",
        documento="20-12345678-9",
        limite_credito=2000
    )

    producto = Producto(
        "P1",
        "Bife",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )
    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 10

    venta = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente
    )

    # Venta a crédito
    venta.agregar_item(
        producto, 1.0, TipoPresentacion.POR_PESO, 1000
    )
    venta.cerrar()

    # Se genera deuda
    assert cliente.saldo_deudor == 1000

    # Se cancela la venta
    venta.cancelar(fecha_actual=venta.fecha)

    # 🔥 EXPECTATIVA CLAVE
    assert cliente.saldo_deudor == 0
