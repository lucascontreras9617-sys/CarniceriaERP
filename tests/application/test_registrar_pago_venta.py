from datetime import date
import pytest

from core.application.use_cases.registrar_pago_venta import RegistrarPagoVenta
from core.application.exceptions.venta_exceptions import VentaNoEncontradaError
from core.domain.exceptions.venta_exceptions import VentaNoCancelableError

from core.domain.entities.venta import Venta
from core.domain.value_objects.dinero import Dinero
from core.domain.value_objects.tipo_pago import TipoPago
from core.domain.value_objects.estado_venta import EstadoVenta

from tests.application.fakes.fake_venta_repository import FakeVentaRepository
from tests.application.fakes.fake_cliente import FakeCliente


# -------------------------------------------------
# Helper
# -------------------------------------------------

def crear_venta_cerrada_con_total(total: int) -> Venta:
    venta = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=FakeCliente(),
    )

    venta.total = Dinero(total)
    venta.deuda_generada = Dinero(total)
    venta.estado = EstadoVenta.CERRADA

    return venta


# -------------------------------------------------
# Tests
# -------------------------------------------------

def test_registrar_pago_exitoso_guarda_venta():
    repo = FakeVentaRepository()
    venta = crear_venta_cerrada_con_total(1000)
    venta.id = "V-1"

    repo.ventas[venta.id] = venta

    caso = RegistrarPagoVenta(repo)

    caso.ejecutar(
        venta_id=venta.id,
        monto=Dinero(400),
        fecha=date(2025, 1, 1),
    )

    assert venta in repo.guardadas
    assert venta.saldo_pendiente() == Dinero(600)


def test_falla_si_venta_no_existe():
    repo = FakeVentaRepository()
    caso = RegistrarPagoVenta(repo)

    with pytest.raises(VentaNoEncontradaError):
        caso.ejecutar(
            venta_id="INEXISTENTE",
            monto=Dinero(100),
            fecha=date.today(),
        )


def test_pago_excesivo_no_guarda():
    repo = FakeVentaRepository()
    venta = crear_venta_cerrada_con_total(300)
    venta.id = "V-2"

    repo.ventas[venta.id] = venta

    caso = RegistrarPagoVenta(repo)

    with pytest.raises(VentaNoCancelableError):
        caso.ejecutar(
            venta_id=venta.id,
            monto=Dinero(500),
            fecha=date.today(),
        )

    assert repo.guardadas == []
