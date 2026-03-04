import pytest
from datetime import date

from core.domain.entities.venta import Venta
from core.domain.value_objects.tipo_pago import TipoPago
from core.domain.entities.cliente import ClienteCrediticio
from core.domain.exceptions.venta_exceptions import VentaNoCancelableError
from core.domain.value_objects.estado_venta import EstadoVenta


def test_venta_saldada_no_se_puede_cancelar():
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

    venta.estado = EstadoVenta.SALDADA

    with pytest.raises(VentaNoCancelableError):
        venta.cancelar(date.today())
    import pytest
from datetime import date

from core.domain.entities.venta import Venta
from core.domain.value_objects.tipo_pago import TipoPago
from core.domain.entities.cliente import ClienteCrediticio
from core.domain.exceptions.venta_exceptions import VentaNoCancelableError
from core.domain.value_objects.estado_venta import EstadoVenta


def test_venta_saldada_no_se_puede_cancelar():
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

    venta.estado = EstadoVenta.SALDADA

    with pytest.raises(VentaNoCancelableError):
        venta.cancelar(date.today())
import pytest
from datetime import date

from core.domain.entities.venta import Venta
from core.domain.value_objects.tipo_pago import TipoPago
from core.domain.entities.cliente import ClienteCrediticio
from core.domain.exceptions.venta_exceptions import VentaNoCancelableError
from core.domain.value_objects.estado_venta import EstadoVenta


def test_venta_saldada_no_se_puede_cancelar():
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

    venta.estado = EstadoVenta.SALDADA

    with pytest.raises(VentaNoCancelableError) as exc:
        venta.cancelar(date.today())

    assert type(exc.value) is VentaNoCancelableError
