import pytest

from core.application.use_cases.registrar_merma import RegistrarMerma
from core.domain.entities.stock import Stock
from core.domain.value_objects.peso import Peso
from core.domain.value_objects.dinero import Dinero
from core.domain.exceptions import ValorInvalidoError

from tests.application.fakes.fake_stock_repository import FakeStockRepository

def test_registrar_merma_reduce_stock_y_genera_movimiento():
    stock_repo = FakeStockRepository()

    stock = Stock.crear_por_peso(
        producto_id="prod-1",
        cantidad_inicial=Peso(10),
        costo_unitario=Dinero(100),
    )

    stock_repo.agregar(stock)

    use_case = RegistrarMerma(stock_repo)

    use_case.ejecutar(
        producto_id="prod-1",
        cantidad=Peso(2),
        motivo="Producto vencido"
    )

    stock_actualizado = stock_repo.obtener_por_producto("prod-1")

    assert stock_actualizado.cantidad.valor == 8
    assert stock_actualizado.movimientos[-1].tipo == "MERMA"

def test_merma_no_puede_dejar_stock_negativo():
    stock_repo = FakeStockRepository()

    stock = Stock.crear_por_peso(
        producto_id="prod-1",
        cantidad_inicial=Peso(1),
        costo_unitario=Dinero(100),
    )

    stock_repo.agregar(stock)

    use_case = RegistrarMerma(stock_repo)

    with pytest.raises(ValorInvalidoError):
        use_case.ejecutar(
            producto_id="prod-1",
            cantidad=Peso(5),
            motivo="Error de frío"
        )
def test_merma_requiere_motivo():
    stock_repo = FakeStockRepository()

    stock = Stock.crear_por_peso(
        producto_id="prod-1",
        cantidad_inicial=Peso(10),
        costo_unitario=Dinero(100),
    )

    stock_repo.agregar(stock)

    use_case = RegistrarMerma(stock_repo)

    with pytest.raises(ValorInvalidoError):
        use_case.ejecutar(
            producto_id="prod-1",
            cantidad=Peso(1),
            motivo=""
        )
