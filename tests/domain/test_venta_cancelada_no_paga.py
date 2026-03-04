import pytest
from datetime import date

from core.domain.entities.venta import Venta
from core.domain.entities.pago import Pago
from core.domain.value_objects.tipo_pago import TipoPago
from core.domain.exceptions.venta_exceptions import VentaNoCancelableError
from core.domain.value_objects.estado_venta import EstadoVenta


def test_venta_cancelada_no_acepta_pagos():
    venta = Venta(tipo_pago=TipoPago.EFECTIVO)
    venta.estado = EstadoVenta.CANCELADA

    with pytest.raises(VentaNoCancelableError):
        venta.registrar_pago(Pago(100, date.today()))
