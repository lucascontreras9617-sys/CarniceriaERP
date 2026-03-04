import pytest
from datetime import date

from core.domain.entities.venta import Venta
from core.domain.entities.pago import Pago
from core.domain.value_objects.tipo_pago import TipoPago
from core.domain.exceptions.venta_exceptions import VentaNoCancelableError


def test_no_se_puede_pagar_venta_abierta():
    venta = Venta(tipo_pago=TipoPago.EFECTIVO)

    with pytest.raises(VentaNoCancelableError):
        venta.registrar_pago(Pago(100, date.today()))


