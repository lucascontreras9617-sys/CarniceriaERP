import pytest

from core.application.use_cases.cerrar_venta import CerrarVenta
from tests.application.fakes.fake_venta_repository import FakeVentaRepository
from core.domain.entities.venta import Venta
from tests.application.fakes.fake_producto import FakeProducto
from core.domain.value_objects.presentacion import Presentacion
from core.domain.value_objects.presentacion import TipoPresentacion
from core.domain.value_objects.dinero import Dinero
from core.domain.value_objects.estado_venta import EstadoVenta
from core.domain.value_objects.peso import Peso
from core.domain.value_objects.cantidad import Cantidad

def crear_venta_abierta():
    venta = Venta()
    producto = FakeProducto()

    venta.agregar_item(
        producto=producto,
        cantidad=Peso (1.000),  # ✅
        precio_unitario=Dinero(100),
        presentacion=Presentacion(TipoPresentacion.POR_PESO),  # ✅
    )

    return venta



def test_cerrar_venta_exitoso_guarda():
    repo = FakeVentaRepository()
    venta = crear_venta_abierta()
    repo.guardar(venta)

    caso_uso = CerrarVenta(repo)
    caso_uso.ejecutar(venta.id)

    assert venta.estado == EstadoVenta.CERRADA
    assert venta in repo.guardadas


def test_error_si_venta_no_existe():
    repo = FakeVentaRepository()
    caso_uso = CerrarVenta(repo)

    with pytest.raises(Exception):
        caso_uso.ejecutar("inexistente")


def test_error_de_dominio_se_propagada():
    repo = FakeVentaRepository()
    venta = Venta()
    venta.id = "v1"
    repo.guardar(venta)

    caso_uso = CerrarVenta(repo)

    with pytest.raises(Exception):
        caso_uso.ejecutar("v1")
