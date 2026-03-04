import pytest

from core.application.use_cases.registrar_egreso_stock import RegistrarEgresoStock
from core.domain.exceptions.stock_exceptions import (
    StockNoEncontradoError,
    StockInsuficienteError,
)
from core.domain.exceptions import ValorInvalidoError
from core.domain.entities.stock import Stock
from core.domain.value_objects.peso import Peso
from core.domain.value_objects.dinero import Dinero

from tests.application.fakes.fake_stock_repository import FakeStockRepository

def test_egresa_stock_y_registra_movimiento():
    stock_repo = FakeStockRepository()

    stock = Stock.crear_por_peso(
        producto_id="prod-1",
        cantidad_inicial=Peso(10),
        costo_unitario=Dinero(100),
    )
    stock_repo.agregar(stock)

    use_case = RegistrarEgresoStock(stock_repository=stock_repo)

    use_case.ejecutar(
        producto_id="prod-1",
        cantidad=Peso(3),
        referencia="Ajuste manual",
    )

    stock_actualizado = stock_repo.obtener_por_producto("prod-1")

    assert stock_actualizado.cantidad.valor == 7
    assert len(stock_actualizado.movimientos) == 2
    assert stock_actualizado.movimientos[-1].tipo == "EGRESO"

def test_error_si_stock_no_existe():
    stock_repo = FakeStockRepository()
    use_case = RegistrarEgresoStock(stock_repository=stock_repo)

    with pytest.raises(StockNoEncontradoError):
        use_case.ejecutar(
            producto_id="prod-x",
            cantidad=Peso(1),
            referencia="Salida",
        )

def test_error_si_stock_insuficiente():
    stock_repo = FakeStockRepository()

    stock = Stock.crear_por_peso(
        producto_id="prod-1",
        cantidad_inicial=Peso(2),
        costo_unitario=Dinero(100),
    )
    stock_repo.agregar(stock)

    use_case = RegistrarEgresoStock(stock_repository=stock_repo)

    with pytest.raises(StockInsuficienteError):
        use_case.ejecutar(
            producto_id="prod-1",
            cantidad=Peso(5),
            referencia="Salida excesiva",
        )

def test_no_permite_egresar_cantidad_invalida():
    stock_repo = FakeStockRepository()

    stock = Stock.crear_por_peso(
        producto_id="prod-1",
        cantidad_inicial=Peso(5),
        costo_unitario=Dinero(100),
    )
    stock_repo.agregar(stock)

    use_case = RegistrarEgresoStock(stock_repository=stock_repo)

    with pytest.raises(ValorInvalidoError):
        use_case.ejecutar(
            producto_id="prod-1",
            cantidad=Peso(0),
            referencia="Error",
        )
