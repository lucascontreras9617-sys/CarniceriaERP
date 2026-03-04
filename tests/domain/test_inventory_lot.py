import pytest
from datetime import datetime, date
from core.domain.entities.inventory_lot import InventoryLot
from core.domain.value_objects.peso import Peso
from core.domain.value_objects.dinero import Dinero
from core.domain.exceptions import ValorInvalidoError


def test_consumir_lote_reduce_cantidad():
    lote = InventoryLot(
        id="lot-1",
        producto_id="prod-1",
        cantidad_disponible=Peso(10),
        costo_unitario=Dinero(100),
        fecha_ingreso=datetime.utcnow(),
        fecha_vencimiento=None
    )

    lote.consumir(Peso(3))

    assert lote.cantidad_disponible.valor == Peso(7).valor


def test_no_permite_consumir_mas_de_lo_disponible():
    lote = InventoryLot(
        id="lot-1",
        producto_id="prod-1",
        cantidad_disponible=Peso(5),
        costo_unitario=Dinero(100),
        fecha_ingreso=datetime.utcnow(),
        fecha_vencimiento=None
    )

    with pytest.raises(ValorInvalidoError):
        lote.consumir(Peso(10))


def test_lote_vencido():
    lote = InventoryLot(
        id="lot-1",
        producto_id="prod-1",
        cantidad_disponible=Peso(5),
        costo_unitario=Dinero(100),
        fecha_ingreso=datetime.utcnow(),
        fecha_vencimiento=date(2020, 1, 1)
    )

    assert lote.esta_vencido(date(2025, 1, 1)) is True
