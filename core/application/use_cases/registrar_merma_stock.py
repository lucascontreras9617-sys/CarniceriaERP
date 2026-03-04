from core.domain.exceptions.stock_exceptions import StockNoEncontradoError


class RegistrarMermaStock:
    def __init__(self, stock_repository):
        self.stock_repository = stock_repository

    def ejecutar(self, producto_id: str, cantidad, motivo: str):
        # 1️⃣ Obtener stock
        stock = self.stock_repository.obtener_por_producto(producto_id)
        if stock is None:
            raise StockNoEncontradoError(
                f"No existe stock para el producto {producto_id}"
            )

        # 2️⃣ Registrar merma (reglas viven en dominio)
        stock.registrar_merma(
            cantidad=cantidad,
            motivo=motivo
        )

        # 3️⃣ Persistir
        self.stock_repository.guardar(stock)
