import pytest
from decimal import Decimal

from core.domain.entities.stock import Stock
from core.domain.value_objects.peso import Peso
from core.domain.value_objects.cantidad import Cantidad
from core.domain.value_objects.dinero import Dinero
from core.domain.exceptions import ValorInvalidoError


def crear_stock_inicial_por_peso():
    return Stock.crear_por_peso(
        producto_id="prod-1",
        cantidad_inicial=Peso(Decimal("10.0")),  # 10 kg
        costo_unitario=Dinero(100)
    )


def test_ingresar_stock_aumenta_cantidad_y_registra_movimiento():
    stock = crear_stock_inicial_por_peso()

    stock.ingresar(
        cantidad=Peso(Decimal("2.5")),
        costo_unitario=Dinero(120),
        referencia="Compra proveedor"
    )

    assert stock.cantidad.valor == Decimal("12.5")
    assert len(stock.movimientos) == 2  # inicial + ingreso
    assert stock.movimientos[-1].tipo == "INGRESO"


def test_egresar_stock_disminuye_cantidad_y_registra_movimiento():
    stock = crear_stock_inicial_por_peso()

    stock.egresar(
        cantidad=Peso(Decimal("3.0")),
        referencia="Venta #123"
    )

    assert stock.cantidad.valor == Decimal("7.0")
    assert stock.movimientos[-1].tipo == "EGRESO"


def test_no_se_puede_egresar_mas_stock_del_disponible():
    stock = crear_stock_inicial_por_peso()

    with pytest.raises(ValorInvalidoError):
        stock.egresar(
            cantidad=Peso(Decimal("11.0")),
            referencia="Venta inválida"
        )


def test_registrar_merma_reduce_stock_y_genera_movimiento():
    stock = crear_stock_inicial_por_peso()

    stock.registrar_merma(
        cantidad=Peso(Decimal("1.5")),
        motivo="Carne en mal estado"
    )

    assert stock.cantidad.valor == Decimal("8.5")
    assert stock.movimientos[-1].tipo == "MERMA"


def test_merma_no_puede_dejar_stock_negativo():
    stock = crear_stock_inicial_por_peso()

    with pytest.raises(ValorInvalidoError):
        stock.registrar_merma(
            cantidad=Peso(Decimal("20.0")),
            motivo="Error grave"
        )


def test_merma_requiere_motivo():
    stock = crear_stock_inicial_por_peso()

    with pytest.raises(ValorInvalidoError):
        stock.registrar_merma(
            cantidad=Peso(Decimal("1.0")),
            motivo=""
        )
