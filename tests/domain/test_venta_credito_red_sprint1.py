import pytest
from datetime import date

from core.domain.entities.venta import Venta
from core.domain.entities.producto import Producto
from core.domain.entities.cliente import ClienteContado

from core.domain.value_objects.presentacion import (
    Presentacion,
    TipoPresentacion
)
from core.domain.value_objects.tipo_pago import TipoPago

from core.domain.exceptions.venta_exceptions import ClienteSinCreditoError


def test_cliente_contado_no_puede_comprar_a_credito():
    producto = Producto(
        "P1",
        "Bife",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )
    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 5.0

    cliente = ClienteContado(
        id="C1",
        nombre="Juan Perez",
        documento="20-12345678-9"
    )

    venta = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente
    )

    venta.agregar_item(
        producto, 1.0, TipoPresentacion.POR_PESO, 1000
    )

    with pytest.raises(ClienteSinCreditoError):
        venta.cerrar()

from core.domain.entities.cliente import ClienteCrediticio
from core.domain.exceptions.cliente_exceptions import LimiteCreditoExcedidoError


def test_cliente_crediticio_no_puede_superar_limite():
    producto = Producto(
        "P1",
        "Nalga",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )
    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 10.0

    cliente = ClienteCrediticio(
        id="C2",
        nombre="Restaurante Don Pepe",
        documento="30-99999999-1",
        limite_credito=1000.0
    )

    venta = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente
    )

    venta.agregar_item(
        producto, 2.0, TipoPresentacion.POR_PESO, 600  # total 1200
    )

    with pytest.raises(LimiteCreditoExcedidoError):
        venta.cerrar()

def test_venta_credito_registra_y_revierte_saldo():
    producto = Producto(
        "P1",
        "Bife",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )
    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 5.0

    cliente = ClienteCrediticio(
        id="C3",
        nombre="Parrilla El Asador",
        documento="30-88888888-2",
        limite_credito=5000.0
    )

    venta = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente
    )

    venta.agregar_item(
        producto, 2.0, TipoPresentacion.POR_PESO, 1000  # total 2000
    )

    venta.cerrar()

    assert cliente.saldo_pendiente == 2000.0

    venta.cancelar(fecha_actual=venta.fecha)

    assert cliente.saldo_pendiente == 0.0
