class FakeProducto:
    def __init__(self, id: str = "prod-1"):
        self.id = id

    def reducir_stock(self, cantidad, presentacion):
        # No hace nada: el stock real se maneja por el repositorio
        pass

    def incrementar_stock(self, cantidad, presentacion):
        pass
