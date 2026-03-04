from datetime import date
import pytest

from core.domain.entities.producto import Producto
from core.domain.entities.venta import Venta
from core.domain.value_objects.presentacion import (
    Presentacion,
    TipoPresentacion
)

def test_venta_descuenta_stock_al_cerrar():
    producto = Producto(
        "P1",
        "Bife",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )
    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 10.0

    venta = Venta()
    venta.agregar_item(
        producto, 2.5, TipoPresentacion.POR_PESO, 1000
    )

    venta.cerrar()

    assert producto.stock_por_presentacion[TipoPresentacion.POR_PESO] == 7.5


def test_venta_cancelada_revierte_stock():
    producto = Producto(
        "P1",
        "Nalga",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )
    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 5.0

    venta = Venta()
    venta.agregar_item(
        producto, 2.0, TipoPresentacion.POR_PESO, 900
    )
    venta.cerrar()

    venta.cancelar(fecha_actual=venta.fecha)

    assert producto.stock_por_presentacion[TipoPresentacion.POR_PESO] == 5.0

def test_no_se_puede_agregar_item_a_venta_cerrada():
    producto = Producto(
        "P1",
        "Bife",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )
    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 10

    venta = Venta(tipo_pago=TipoPago.EFECTIVO)

    venta.agregar_item(
        producto, 1.0, TipoPresentacion.POR_PESO, 1000
    )
    venta.cerrar()

    with pytest.raises(VentaCerradaError):
        venta.agregar_item(
            producto, 1.0, TipoPresentacion.POR_PESO, 1000
        )
