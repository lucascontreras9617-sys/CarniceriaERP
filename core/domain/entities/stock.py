from datetime import datetime
from uuid import uuid4
from decimal import Decimal

from core.domain.entities.movimiento_stock import MovimientoStock
from core.domain.entities.inventory_lot import InventoryLot
from core.domain.exceptions import ValorInvalidoError
from core.domain.exceptions.stock_exceptions import StockInsuficienteError
from core.domain.value_objects.peso import Peso
from core.domain.value_objects.dinero import Dinero
from core.domain.value_objects.consumo_lote import ConsumoLote


class Stock:
    def __init__(self, producto_id: str):
        self.producto_id = producto_id
        self.movimientos: list[MovimientoStock] = []
        self.lots: list[InventoryLot] = []

    # =========================================================
    # 📦 Cantidad total (DERIVADA, no VO)
    # =========================================================
    @property
    def cantidad_total(self) -> Decimal:
        return sum(
            (lot.cantidad_disponible.valor for lot in self.lots),
            start=Decimal("0"),
        )

    # =========================================================
    # 🔥 FIFO REAL (motor interno)
    # =========================================================
    def _consumir_lotes(self, cantidad: Peso) -> list[ConsumoLote]:
        restante = cantidad.valor
        consumos: list[ConsumoLote] = []

        lotes_ordenados = sorted(
            self.lots,
            key=lambda lot: lot.fecha_ingreso
        )

        total_disponible = sum(
            (lot.cantidad_disponible.valor for lot in lotes_ordenados),
            start=Decimal("0"),
        )

        if restante > total_disponible:
            raise StockInsuficienteError(
                "Stock insuficiente para consumo FIFO"
            )

        for lot in lotes_ordenados:
            if restante <= 0:
                break

            disponible = lot.cantidad_disponible.valor
            if disponible <= 0:
                continue

            if disponible <= restante:
                cantidad_consumida = Peso(disponible)
                lot.consumir(cantidad_consumida)
                restante -= disponible
            else:
                cantidad_consumida = Peso(restante)
                lot.consumir(cantidad_consumida)
                restante = Decimal("0")

            consumos.append(
                ConsumoLote(
                    lote_id=lot.id,
                    cantidad=cantidad_consumida,
                    costo_unitario=lot.costo_unitario,
                )
            )

        return consumos

    # =========================================================
    # 🏭 Factory
    # =========================================================
    @classmethod
    def crear_por_peso(
        cls,
        producto_id: str,
        cantidad_inicial: Peso,
        costo_unitario: Dinero,
        fecha_vencimiento=None,
    ):
        if cantidad_inicial.valor <= 0:
            raise ValorInvalidoError(
                "El stock inicial debe ser mayor a cero"
            )

        stock = cls(producto_id)

        stock.lots.append(
            InventoryLot(
                id=str(uuid4()),
                producto_id=producto_id,
                cantidad_disponible=cantidad_inicial,
                costo_unitario=costo_unitario,
                fecha_ingreso=datetime.utcnow(),
                fecha_vencimiento=fecha_vencimiento,
            )
        )

        stock.movimientos.append(
            MovimientoStock.ingreso(
                cantidad=cantidad_inicial,
                costo_unitario=costo_unitario,
                referencia="Stock inicial",
            )
        )

        return stock

    # =========================================================
    # ➕ Ingreso
    # =========================================================
    def ingresar(
        self,
        cantidad: Peso,
        costo_unitario: Dinero,
        referencia: str,
        fecha_vencimiento=None,
    ):
        if cantidad.valor <= 0:
            raise ValorInvalidoError(
                "La cantidad a ingresar debe ser positiva"
            )

        self.lots.append(
            InventoryLot(
                id=str(uuid4()),
                producto_id=self.producto_id,
                cantidad_disponible=cantidad,
                costo_unitario=costo_unitario,
                fecha_ingreso=datetime.utcnow(),
                fecha_vencimiento=fecha_vencimiento,
            )
        )

        self.movimientos.append(
            MovimientoStock.ingreso(
                cantidad=cantidad,
                costo_unitario=costo_unitario,
                referencia=referencia,
            )
        )

    # =========================================================
    # ➖ Egreso (venta / ajuste)
    # =========================================================
    def egresar(self, cantidad: Peso, referencia: str) -> list[ConsumoLote]:
        if cantidad.valor <= 0:
            raise ValorInvalidoError(
                "La cantidad a egresar debe ser positiva"
            )

        consumos = self._consumir_lotes(cantidad)

        self.movimientos.append(
            MovimientoStock.egreso(
                cantidad=cantidad,
                referencia=referencia,
            )
        )

        return consumos

    # =========================================================
    # 🧹 Merma (también FIFO)
    # =========================================================
    def registrar_merma(self, cantidad: Peso, motivo: str):
        if not motivo or not motivo.strip():
            raise ValorInvalidoError(
                "La merma requiere un motivo"
            )

        if cantidad.valor <= 0:
            raise ValorInvalidoError(
                "La cantidad de merma debe ser positiva"
            )

        self._consumir_lotes(cantidad)

        self.movimientos.append(
            MovimientoStock.merma(
                cantidad=cantidad,
                motivo=motivo,
            )
        )
