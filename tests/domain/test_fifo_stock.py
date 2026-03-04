from datetime import datetime, timedelta

import pytest

from core.domain.entities.stock import Stock
from core.domain.value_objects.peso import Peso
from core.domain.value_objects.dinero import Dinero
from core.domain.exceptions.stock_exceptions import StockInsuficienteError


def test_fifo_consumo_respeta_orden_de_ingreso():
    stock = Stock.crear_por_peso(
        producto_id="carne",
        cantidad_inicial=Peso(10),
        costo_unitario=Dinero(100),
    )

    # Segundo ingreso más caro y más nuevo
    stock.ingresar(
        cantidad=Peso(10),
        costo_unitario=Dinero(150),
        referencia="Ingreso 2",
    )

    consumos = stock.egresar(Peso(12), referencia="Venta")

    assert len(consumos) == 2

    # Primer lote (FIFO)
    assert consumos[0].cantidad.valor == 10
    assert consumos[0].costo_unitario.monto == 100

    # Segundo lote
    assert consumos[1].cantidad.valor == 2
    assert consumos[1].costo_unitario.monto == 150


def test_fifo_lanza_error_si_stock_insuficiente():
    stock = Stock.crear_por_peso(
        producto_id="carne",
        cantidad_inicial=Peso(5),
        costo_unitario=Dinero(100),
    )

    with pytest.raises(StockInsuficienteError):
        stock.egresar(Peso(10), referencia="Venta")
