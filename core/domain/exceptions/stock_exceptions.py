class StockError(Exception):
    """Excepción base de stock"""
    pass

class StockNoEncontradoError(StockError):
    """No existe stock para el producto solicitado"""
    pass


class StockInsuficienteError(StockError):
    """No hay stock suficiente para realizar la operación"""
    pass
