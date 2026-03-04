import pytest

from core.domain.entities.cliente import ClienteCrediticio
from core.domain.entities.producto import Producto
from core.domain.entities.venta import Venta
from core.domain.value_objects.presentacion import (
    Presentacion,
    TipoPresentacion
)
from core.domain.value_objects.tipo_pago import TipoPago


def test_credito_se_calcula_por_importe_no_por_presentacion():
    cliente = ClienteCrediticio(
        id="C1",
        nombre="Juan Perez",
        documento="20-12345678-9",
        limite_credito=5000
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

    # Venta por peso
    venta1 = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente
    )
    venta1.agregar_item(
        producto_peso, 1.0, TipoPresentacion.POR_PESO, 1000
    )
    venta1.cerrar()

    # Venta por unidad
    venta2 = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente
    )
    venta2.agregar_item(
        producto_unidad, 1, TipoPresentacion.POR_UNIDAD, 1000
    )
    venta2.cerrar()

    # 🔥 Lo importante
    assert cliente.saldo_deudor == 2000
