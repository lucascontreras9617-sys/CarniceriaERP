# core/domain/entities/producto.py

from core.domain.value_objects.presentacion import (
    Presentacion,
    TipoPresentacion
)
from core.domain.exceptions.producto_exceptions import (
    StockInsuficienteError,
    PresentacionNoDisponibleError
)

class Producto:

    def __init__(self, id, nombre, presentaciones):
        self.id = id
        self.nombre = nombre
        self.presentaciones = presentaciones
        self.stock_por_presentacion = {
            p.tipo: 0.0 for p in presentaciones
        }

    def tiene_presentacion(self, tipo: TipoPresentacion) -> bool:
        return any(p.tipo == tipo for p in self.presentaciones)

    def obtener_presentacion(self, tipo: TipoPresentacion) -> Presentacion:
        for p in self.presentaciones:
            if p.tipo == tipo:
                return p
        raise PresentacionNoDisponibleError(
            f"{self.nombre} no tiene presentación {tipo.value}"
        )

    def reducir_stock(
        self,
        cantidad: float,
        tipo: TipoPresentacion
    ) -> None:
        presentacion = self.obtener_presentacion(tipo)

        # 🔒 La presentación valida la cantidad
        presentacion.validar_cantidad(cantidad)

        disponible = self.stock_por_presentacion[tipo]
        if disponible < cantidad:
            raise StockInsuficienteError(
                self.nombre,
                disponible,
                cantidad
            )

        self.stock_por_presentacion[tipo] -= cantidad

    def incrementar_stock(
        self,
        cantidad: float,
        tipo: TipoPresentacion
    ) -> None:
        self.stock_por_presentacion[tipo] += cantidad
