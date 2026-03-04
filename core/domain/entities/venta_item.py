# app/dominio/entities/venta_item.py
import uuid
from ..value_objects import Dinero, Cantidad
from ..exceptions import ValorInvalidoError

class VentaItem:
    """
    Item individual dentro de una venta.
    Representa un producto específico con cantidad y precio.
    """
    
    def __init__(
        self,
        producto,
        cantidad_kg: float,
        precio_kg: float
    ):
        self.id = str(uuid.uuid4())
        self.producto = producto
        
        # Validar y convertir a Value Objects
        if cantidad_kg <= 0:
            raise ValorInvalidoError("La cantidad debe ser positiva")
        
        if precio_kg <= 0:
            raise ValorInvalidoError("El precio debe ser positivo")
        
        self.cantidad = Cantidad(cantidad_kg, 'kg')
        self.precio_unitario = Dinero(precio_kg)
        self.subtotal = self.cantidad * self.precio_unitario
    
    @property
    def nombre_producto(self):
        return self.producto.nombre
    
    @property
    def cantidad_kg(self):
        return self.cantidad.valor
    
    @property
    def precio_kg(self):
        return self.precio_unitario.monto
    
    def calcular_subtotal(self):
        """Recalcula subtotal (útil si cambian cantidad o precio)"""
        self.subtotal = self.cantidad * self.precio_unitario
        return self.subtotal
    
    def __repr__(self):
        return (
            f"VentaItem(producto='{self.nombre_producto}', "
            f"cantidad={self.cantidad}, precio={self.precio_unitario}, "
            f"subtotal={self.subtotal})"
        )
    
    def __str__(self):
        return f"{self.nombre_producto}: {self.cantidad} × {self.precio_unitario} = {self.subtotal}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'producto_id': self.producto.id,
            'producto_nombre': self.nombre_producto,
            'cantidad_kg': self.cantidad_kg,
            'precio_kg': self.precio_kg,
            'subtotal': self.subtotal.monto
        }