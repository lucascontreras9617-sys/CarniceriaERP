import pytest

from core.domain.entities.venta import Venta
from core.domain.entities.producto import Producto
from core.domain.exceptions.venta_exceptions import VentaSinItemsError
from core.domain.value_objects.presentacion import (
    Presentacion,
    TipoPresentacion
)


def test_no_se_puede_cerrar_venta_sin_items():
    """
    Regla: una venta sin items no puede cerrarse.
    """
    venta = Venta()

    with pytest.raises(VentaSinItemsError):
        venta.cerrar()


def test_venta_pasa_de_abierta_a_cerrada():
    """
    Regla: al cerrarse, la venta debe cambiar su estado a CERRADA.
    """
    producto = Producto(
        "P1",
        "Bife de Chorizo",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )

    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 10.0

    venta = Venta()

    venta.agregar_item(
        producto=producto,
        cantidad=1.0,
        presentacion=TipoPresentacion.POR_PESO,
        precio_unitario=1000.0
    )

    venta.cerrar()

    assert venta.estado.name == "CERRADA"


def test_total_venta_se_calcula_correctamente():
    """
    Regla: el total de la venta es la suma de los subtotales de sus items.
    """
    producto = Producto(
        "P1",
        "Bife de Chorizo",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )

    venta = Venta()

    venta.agregar_item(
        producto=producto,
        cantidad=2.0,
        presentacion=TipoPresentacion.POR_PESO,
        precio_unitario=1000.0
    )

    venta.agregar_item(
        producto=producto,
        cantidad=1.5,
        presentacion=TipoPresentacion.POR_PESO,
        precio_unitario=1200.0
    )

    assert venta.total == (2.0 * 1000.0) + (1.5 * 1200.0)
