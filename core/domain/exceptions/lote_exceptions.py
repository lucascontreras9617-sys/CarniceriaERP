"""
Excepciones específicas del agregado Lote
"""

class LoteNoEncontradoError(Exception):
    """Lanzada cuando un lote no existe"""
    pass


class StockInsuficienteError(Exception):
    """Lanzada cuando no hay suficiente stock"""
    pass
