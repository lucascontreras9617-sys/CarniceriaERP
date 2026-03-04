import pytest

from core.application.use_cases.registrar_ingreso_stock import RegistrarIngresoStock

from core.domain.entities.stock import Stock
from core.domain.value_objects.peso import Peso
from core.domain.value_objects.dinero import Dinero
from core.domain.exceptions.stock_exceptions import StockNoEncontradoError
from core.domain.exceptions import ValorInvalidoError

from tests.application.fakes.fake_stock_repository import FakeStockRepository


def test_ingresa_stock_existente_y_registra_movimiento():
    stock_repo = FakeStockRepository()

    stock = Stock.crear_por_peso(
        producto_id="prod-1",
        cantidad_inicial=Peso(10),
        costo_unitario=Dinero(100),
    )
    stock_repo.agregar(stock)

    use_case = RegistrarIngresoStock(stock_repository=stock_repo)

    use_case.ejecutar(
        producto_id="prod-1",
        cantidad=Peso(5),
        costo_unitario=Dinero(120),
        referencia="Compra proveedor A"
    )

    stock_actualizado = stock_repo.obtener_por_producto("prod-1")

    assert stock_actualizado.cantidad.valor == 15
    assert len(stock_actualizado.movimientos) == 2
    assert stock_actualizado.movimientos[-1].tipo == "INGRESO"


def test_crea_stock_si_no_existe():
    stock_repo = FakeStockRepository()

    use_case = RegistrarIngresoStock(stock_repository=stock_repo)

    use_case.ejecutar(
        producto_id="prod-2",
        cantidad=Peso(8),
        costo_unitario=Dinero(90),
        referencia="Compra inicial"
    )

    stock = stock_repo.obtener_por_producto("prod-2")

    assert stock is not None
    assert stock.cantidad.valor == 8
    assert len(stock.movimientos) == 1
    assert stock.movimientos[0].tipo == "INGRESO"


def test_no_permite_ingresar_cantidad_invalida():
    stock_repo = FakeStockRepository()

    use_case = RegistrarIngresoStock(stock_repository=stock_repo)

    with pytest.raises(ValorInvalidoError):
        use_case.ejecutar(
            producto_id="prod-3",
            cantidad=Peso(0),
            costo_unitario=Dinero(100),
            referencia="Compra inválida"
        )
