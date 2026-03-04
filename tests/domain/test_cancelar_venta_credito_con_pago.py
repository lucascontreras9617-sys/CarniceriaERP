import pytest
from datetime import date

from core.domain.entities.cliente import ClienteCrediticio
from core.domain.entities.producto import Producto
from core.domain.entities.venta import Venta
from core.domain.value_objects.tipo_pago import TipoPago
from core.domain.value_objects.presentacion import TipoPresentacion
from core.domain.value_objects.presentacion import Presentacion
from core.domain.exceptions.venta_exceptions import VentaNoCancelableError


def test_no_se_puede_cancelar_venta_credito_con_pagos():
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
    

    venta.agregar_item(
        producto, 1.0, TipoPresentacion.POR_PESO, 1000
    )
    venta.cerrar()

    # Pago parcial
    cliente.pagar(400)

    # 🔥 No debería poder cancelarse
    with pytest.raises(VentaNoCancelableError):
        venta.cancelar(fecha_actual=venta.fecha)
