from datetime import date
import pytest

from core.domain.entities.producto import Producto
from core.domain.entities.venta import Venta

from core.domain.value_objects.presentacion import (
    Presentacion,
    TipoPresentacion
)

from core.domain.exceptions.producto_exceptions import StockInsuficienteError
from core.domain.exceptions.venta_exceptions import (
    VentaCerradaError,
    VentaFueraDePlazoError
)


def test_no_se_puede_cerrar_venta_con_stock_insuficiente():
    producto = Producto(
        "P1",
        "Bife",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )

    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 1.0

    venta = Venta()
    venta.agregar_item(
        producto=producto,
        cantidad=2.0,  # ❌ más de lo disponible
        presentacion=TipoPresentacion.POR_PESO,
        precio_unitario=1000
    )

    with pytest.raises(StockInsuficienteError):
        venta.cerrar()


def test_no_se_puede_agregar_item_a_venta_cerrada():
    producto = Producto(
        "P1",
        "Bife",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )

    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 10.0

    venta = Venta()
    venta.agregar_item(
        producto, 1.0, TipoPresentacion.POR_PESO, 1000
    )
    venta.cerrar()

    with pytest.raises(VentaCerradaError):
        venta.agregar_item(
            producto, 1.0, TipoPresentacion.POR_PESO, 1000
        )


def test_no_se_puede_cancelar_venta_fuera_de_plazo():
    producto = Producto(
        "P1",
        "Bife",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )

    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 5.0

    venta = Venta(fecha=date(2025, 1, 1))
    venta.agregar_item(
        producto, 1.0, TipoPresentacion.POR_PESO, 1000
    )
    venta.cerrar()

    with pytest.raises(VentaFueraDePlazoError):
        venta.cancelar(fecha_actual=date(2025, 1, 3))
