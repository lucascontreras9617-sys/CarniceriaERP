from datetime import date

import pytest

from core.domain.entities.venta import Venta
from core.domain.entities.cliente import ClienteCrediticio
from core.domain.entities.producto import Producto   # ✅ ESTE FALTABA
from core.domain.entities.pago import Pago
from core.domain.exceptions.venta_exceptions import VentaNoCancelableError
from core.domain.value_objects.tipo_pago import TipoPago
from core.domain.value_objects.presentacion import Presentacion, TipoPresentacion
from core.domain.value_objects.estado_venta import EstadoVenta

def test_venta_registra_pagos():
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
        producto,
        1.0,
        TipoPresentacion.POR_PESO,
        1000
    )

    venta.cerrar()   # ✅ genera deuda (saldo_deudor = 1000)

    pago = Pago(monto=500, fecha=date.today())

    venta.registrar_pago(pago)

    assert len(venta.pagos) == 1
    assert cliente.saldo_deudor == 500

def test_no_se_puede_pagar_venta_cancelada():
    cliente = ClienteCrediticio(
        id="C1",
        nombre="Juan Perez",
        documento="20-12345678-9",
        limite_credito=2000
    )

    venta = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente
    )

    venta.estado = EstadoVenta.CANCELADA

    with pytest.raises(VentaNoCancelableError):
        venta.registrar_pago(Pago(500, date.today()))

def test_no_se_puede_pagar_venta_saldada():
    cliente = ClienteCrediticio(
        id="C1",
        nombre="Juan Perez",
        documento="20-12345678-9",
        limite_credito=5000
    )

    venta = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente
    )

    # Forzamos estado SALDADA (no nos interesa cómo llegó ahí)
    venta.estado = EstadoVenta.SALDADA

    with pytest.raises(VentaNoCancelableError):
        venta.registrar_pago(Pago(100, date.today()))