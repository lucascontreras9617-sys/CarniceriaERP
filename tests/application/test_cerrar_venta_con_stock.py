import pytest

from core.application.use_cases.cerrar_venta import CerrarVenta

from core.domain.entities.venta import Venta
from core.domain.entities.stock import Stock

from core.domain.value_objects.peso import Peso
from core.domain.value_objects.dinero import Dinero
from core.domain.value_objects.presentacion import (
    Presentacion,
    TipoPresentacion,
)
from core.domain.value_objects.estado_venta import EstadoVenta
from tests.application.fakes.fake_venta_repository import FakeVentaRepository
from tests.application.fakes.fake_stock_repository import FakeStockRepository
from tests.application.fakes.fake_producto import FakeProducto


def test_cerrar_venta_egresa_stock_y_cierra_venta():
    # Repositorios fake
    venta_repo = FakeVentaRepository()
    stock_repo = FakeStockRepository()

    # Producto
    producto = FakeProducto(id="prod-1")

    # Stock inicial: 10 kg
    stock = Stock.crear_por_peso(
        producto_id="prod-1",
        cantidad_inicial=Peso(10),
        costo_unitario=Dinero(100),
    )
    stock_repo.agregar(stock)

    # Venta abierta con consumo de 2 kg
    venta = Venta()
    venta.agregar_item(
        producto=producto,
        cantidad=Peso(2),
        precio_unitario=Dinero(100),
        presentacion=Presentacion(TipoPresentacion.POR_PESO),
    )

    venta_repo.guardar(venta)

    # Caso de uso
    use_case = CerrarVenta(
        venta_repository=venta_repo,
        stock_repository=stock_repo,
    )

    # Acción
    use_case.ejecutar(venta.id)

    # Assert
    stock_actualizado = stock_repo.obtener_por_producto("prod-1")

    assert stock_actualizado.cantidad.valor == 8
    assert venta.estado == EstadoVenta.CERRADA


def test_no_cierra_venta_si_stock_insuficiente():
    # Repositorios fake
    venta_repo = FakeVentaRepository()
    stock_repo = FakeStockRepository()

    # Producto
    producto = FakeProducto(id="prod-1")

    # Stock inicial: 1 kg
    stock = Stock.crear_por_peso(
        producto_id="prod-1",
        cantidad_inicial=Peso(1),
        costo_unitario=Dinero(100),
    )
    stock_repo.agregar(stock)

    # Venta intenta consumir 5 kg (más de lo disponible)
    venta = Venta()
    venta.agregar_item(
        producto=producto,
        cantidad=Peso(5),
        precio_unitario=Dinero(100),
        presentacion=Presentacion(TipoPresentacion.POR_PESO),
    )

    venta_repo.guardar(venta)

    # Caso de uso
    use_case = CerrarVenta(
        venta_repository=venta_repo,
        stock_repository=stock_repo,
    )

    # Acción + Assert
    with pytest.raises(Exception):
        use_case.ejecutar(venta.id)

    # La venta NO debe cerrarse
    assert venta.estado == EstadoVenta.ABIERTA
