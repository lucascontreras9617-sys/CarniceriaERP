import pytest

from core.domain.entities.cliente import ClienteCrediticio
from core.domain.entities.producto import Producto
from core.domain.entities.venta import Venta
from core.domain.value_objects.presentacion import Presentacion, TipoPresentacion
from core.domain.value_objects.tipo_pago import TipoPago
from core.domain.exceptions.cliente_exceptions import LimiteCreditoExcedidoError


def test_venta_credito_con_presentaciones_mixtas():
    cliente = ClienteCrediticio(
        id="C1",
        nombre="Juan Perez",
        documento="20-12345678-9",
        limite_credito=3000
    )

    producto_peso = Producto(
        "P1",
        "Bife",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )
    producto_peso.stock_por_presentacion[TipoPresentacion.POR_PESO] = 10

    producto_unidad = Producto(
        "P2",
        "Chorizo",
        [Presentacion(TipoPresentacion.POR_UNIDAD)]
    )
    producto_unidad.stock_por_presentacion[TipoPresentacion.POR_UNIDAD] = 10

    venta = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente
    )

    # 1 kg de bife → $1200
    venta.agregar_item(
        producto_peso, 1.0, TipoPresentacion.POR_PESO, 1200
    )

    # 2 chorizos → $800
    venta.agregar_item(
        producto_unidad, 2, TipoPresentacion.POR_UNIDAD, 400
    )

    venta.cerrar()

    # 🔥 Crédito total: 1200 + 800 = 2000
    assert cliente.saldo_deudor == 2000
