import pytest
from datetime import date

from core.domain.entities.venta import Venta
from core.domain.entities.cliente import ClienteCrediticio
from core.domain.entities.producto import Producto
from core.domain.entities.pago import Pago
from core.domain.value_objects.tipo_pago import TipoPago
from core.domain.value_objects.presentacion import Presentacion, TipoPresentacion
from core.domain.exceptions.venta_exceptions import VentaNoCancelableError


def test_no_se_puede_pagar_una_venta_ya_saldada():
    cliente = ClienteCrediticio(
        id="C1",
        nombre="Juan Perez",
        documento="20-12345678-9",
        limite_credito=5000
    )

    producto = Producto(
        "P1",
        "Bife",
        [Presentacion(TipoPresentacion.POR_PESO)]
    )
    producto.stock_por_presentacion[TipoPresentacion.POR_PESO] = 10

    venta = Venta(
        tipo_pago=TipoPago.CREDITO,
        cliente=cliente
    )

    venta.agregar_item(
        producto, 1.0, TipoPresentacion.POR_PESO, 1000
    )
    venta.cerrar()

    # Pago total → venta saldada
    venta.registrar_pago(Pago(1000, date.today()))

    # 🔥 Intento de nuevo pago
    with pytest.raises(VentaNoCancelableError):
        venta.registrar_pago(Pago(100, date.today()))
