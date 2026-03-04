from datetime import date
import pytest

from core.domain.entities.producto import Producto
from core.domain.entities.venta import Venta
from core.domain.entities.cliente import ClienteCrediticio
from core.domain.value_objects.estado_venta import EstadoVenta
from core.domain.exceptions.cliente_exceptions import PagoInvalidoError
from core.domain.value_objects.presentacion import (
    Presentacion,
    TipoPresentacion
)
from core.domain.value_objects.tipo_pago import TipoPago

from core.domain.exceptions.cliente_exceptions import (
    LimiteCreditoExcedidoError
)


def test_cliente_crediticio_no_puede_superar_limite_de_credito():
    """
    Regla: un cliente crediticio no puede cerrar una venta
    cuyo total supere su límite de crédito.
    """

    producto = Producto(
        "P1",
        "Bife de Chorizo",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )
    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 10.0

    cliente = ClienteCrediticio(
        id="C2",
        nombre="Carlos Gomez",
        documento="20-98765432-1",
        limite_credito=5000.0
    )

    venta = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente,
        fecha=date(2025, 1, 10)
    )

    venta.agregar_item(
        producto,
        cantidad=6.0,          # 6 kg
        presentacion=TipoPresentacion.POR_PESO,
        precio_unitario=1000   # total = 6000
    )

    with pytest.raises(LimiteCreditoExcedidoError):
        venta.cerrar()

def test_cliente_crediticio_puede_comprar_dentro_del_limite():
    producto = Producto(
        "P1",
        "Bife",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )
    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 5.0

    cliente = ClienteCrediticio(
        id="C1",
        nombre="Juan Perez",
        documento="20-12345678-9",
        limite_credito=2000
    )

    venta = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente
    )

    venta.agregar_item(
        producto, 1.0, TipoPresentacion.POR_PESO, 1000
    )

    venta.cerrar()

    assert venta.estado == EstadoVenta.CERRADA

def test_cliente_crediticio_no_puede_superar_limite_credito():
    producto = Producto(
        "P1",
        "Bife",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )
    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 10.0

    cliente = ClienteCrediticio(
        id="C2",
        nombre="Ana Gomez",
        documento="27-98765432-1",
        limite_credito=1000,
        saldo_deudor=900
    )

    venta = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente
    )

    venta.agregar_item(
        producto,
        1.0,                      # 1 kg
        TipoPresentacion.POR_PESO,
        200                        # subtotal = 200 → excede límite
    )

    with pytest.raises(LimiteCreditoExcedidoError):
        venta.cerrar()

def test_cliente_crediticio_no_puede_superar_limite_con_varias_ventas():
    producto = Producto(
        "P1",
        "Bife",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )
    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 20.0

    cliente = ClienteCrediticio(
        id="C3",
        nombre="Carlos Lopez",
        documento="30-11111111-1",
        limite_credito=2000
    )

    # Venta 1
    venta1 = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente
    )
    venta1.agregar_item(
        producto, 1.0, TipoPresentacion.POR_PESO, 1200
    )
    venta1.cerrar()

    # Venta 2
    venta2 = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente
    )
    venta2.agregar_item(
        producto, 1.0, TipoPresentacion.POR_PESO, 900
    )

    with pytest.raises(LimiteCreditoExcedidoError):
        venta2.cerrar()

def test_cliente_puede_pagar_parte_de_su_deuda():
    cliente = ClienteCrediticio(
        id="C1",
        nombre="Juan Perez",
        documento="20-12345678-9",
        limite_credito=2000,
        saldo_deudor=1000
    )

    cliente.pagar(400)

    assert cliente.saldo_deudor == 600

def test_cliente_puede_cancelar_toda_su_deuda():
    cliente = ClienteCrediticio(
        id="C4",
        nombre="Laura Diaz",
        documento="27-22222222-9",
        limite_credito=1500,
        saldo_deudor=800
    )

    cliente.pagar(800)

    assert cliente.saldo_deudor == 0

def test_cliente_no_puede_pagar_monto_invalido():
    cliente = ClienteCrediticio(
        id="C5",
        nombre="Mario Suarez",
        documento="23-33333333-3",
        limite_credito=3000,
        saldo_deudor=500
    )

    with pytest.raises(PagoInvalidoError):
        cliente.pagar(-100)

    with pytest.raises(PagoInvalidoError):
        cliente.pagar(0)

    with pytest.raises(PagoInvalidoError):
        cliente.pagar(600)
