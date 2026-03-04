import pytest

from core.domain.entities.producto import Producto
from core.domain.value_objects.presentacion import (
    Presentacion,
    TipoPresentacion
)
from core.domain.exceptions.producto_exceptions import CantidadInvalidaError


def test_no_se_puede_vender_fraccion_de_unidad():
    """
    Regla: productos por unidad solo aceptan cantidades enteras.
    """
    producto = Producto(
        "P1",
        "Hamburguesa",
        [Presentacion(TipoPresentacion.POR_UNIDAD)]
    )

    with pytest.raises(CantidadInvalidaError):
        producto.reducir_stock(
            cantidad=1.5,  # ❌ fracción
            tipo=TipoPresentacion.POR_UNIDAD
        )
