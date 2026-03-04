from core.domain.entities.stock import Stock
from core.domain.exceptions.stock_exceptions import StockNoEncontradoError
from core.domain.value_objects.peso import Peso
from core.domain.value_objects.dinero import Dinero


class RegistrarIngresoStock:
    def __init__(self, stock_repository):
        self.stock_repository = stock_repository

    def ejecutar(
        self,
        producto_id: str,
        cantidad: Peso,
        costo_unitario: Dinero,
        referencia: str,
    ) -> None:
        try:
            # 1️⃣ Intentar obtener stock existente
            stock = self.stock_repository.obtener_por_producto(producto_id)

            # 2️⃣ Ingresar stock
            stock.ingresar(
                cantidad=cantidad,
                costo_unitario=costo_unitario,
                referencia=referencia,
            )

        except StockNoEncontradoError:
            # 3️⃣ Crear stock si no existe
            stock = Stock.crear_por_peso(
                producto_id=producto_id,
                cantidad_inicial=cantidad,
                costo_unitario=costo_unitario,
            )

        # 4️⃣ Persistir
        self.stock_repository.guardar(stock)
