# app/dominio/entities/producto.py
import uuid
from datetime import datetime
from typing import Optional
from ..value_objects import Dinero, Cantidad
from ..exceptions import StockInsuficienteError, ProductoInactivoError, ValorInvalidoError

class Producto:
    """
    Entidad de dominio Producto.
    Contiene toda la lógica de negocio relacionada con productos.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        nombre: str = "",
        precio_venta: Dinero = None,
        stock_actual: Cantidad = None,
        costo_ultima_compra: Dinero = None,
        tipo: str = "ROTACION",
        activo: bool = True
    ):
        self.id = id or str(uuid.uuid4())
        self.nombre = nombre
        self.precio_venta = precio_venta or Dinero.zero()
        self.stock_actual = stock_actual or Cantidad.zero('kg')
        self.costo_ultima_compra = costo_ultima_compra or Dinero.zero()
        self.tipo = tipo  # ROTACION, PREMIUM, BAJO_VALOR
        self.activo = activo
        
        # Audit fields
        self.fecha_creacion = datetime.now()
        self.fecha_ultima_actualizacion = datetime.now()
    
    # ============ LÓGICA DE STOCK ============
    
    def tiene_stock_suficiente(self, cantidad_necesaria: Cantidad) -> bool:
        """
        Verifica si hay stock suficiente para una operación.
        Valida que las unidades coincidan.
        """
        if not isinstance(cantidad_necesaria, Cantidad):
            raise TypeError("cantidad_necesaria debe ser tipo Cantidad")
        
        if self.stock_actual.unidad != cantidad_necesaria.unidad:
            raise ValorInvalidoError(
                f"Unidad de stock ({self.stock_actual.unidad}) "
                f"difiere de unidad requerida ({cantidad_necesaria.unidad})"
            )
        
        return self.stock_actual.valor >= cantidad_necesaria.valor
    
    def reducir_stock(self, cantidad: Cantidad):
        """
        Reduce el stock del producto.
        Valida stock suficiente y producto activo.
        """
        if not self.activo:
            raise ProductoInactivoError(f"Producto {self.nombre} está inactivo")
        
        if not isinstance(cantidad, Cantidad):
            raise TypeError("cantidad debe ser tipo Cantidad")
        
        if not self.tiene_stock_suficiente(cantidad):
            raise StockInsuficienteError(
                f"Stock insuficiente: {self.stock_actual} "
                f"< {cantidad} para {self.nombre}"
            )
        
        # Crear nueva cantidad con el stock reducido
        self.stock_actual = Cantidad(
            self.stock_actual.valor - cantidad.valor,
            self.stock_actual.unidad
        )
        
        self.fecha_ultima_actualizacion = datetime.now()
    
    def aumentar_stock(self, cantidad: Cantidad):
        """
        Aumenta el stock del producto.
        """
        if not self.activo:
            raise ProductoInactivoError(f"Producto {self.nombre} está inactivo")
        
        if not isinstance(cantidad, Cantidad):
            raise TypeError("cantidad debe ser tipo Cantidad")
        
        self.stock_actual = Cantidad(
            self.stock_actual.valor + cantidad.valor,
            self.stock_actual.unidad
        )
        
        self.fecha_ultima_actualizacion = datetime.now()
    
    # ============ LÓGICA DE PRECIOS ============
    
    def calcular_precio_con_descuento(self, porcentaje_descuento: float) -> Dinero:
        """
        Calcula precio con descuento aplicado.
        """
        if porcentaje_descuento < 0 or porcentaje_descuento > 100:
            raise ValorInvalidoError("Porcentaje de descuento inválido")
        
        descuento = self.precio_venta * (porcentaje_descuento / 100)
        return self.precio_venta - descuento
    
    def calcular_margen(self) -> float:
        """
        Calcula margen de ganancia porcentual.
        """
        if self.costo_ultima_compra.monto == 0:
            return 0.0
        
        margen_bruto = self.precio_venta.monto - self.costo_ultima_compra.monto
        return (margen_bruto / self.precio_venta.monto) * 100
    
    # ============ VALIDACIONES ============
    
    def validar_para_venta(self) -> bool:
        """
        Verifica si el producto puede ser vendido.
        """
        if not self.activo:
            return False
        
        if self.precio_venta.monto <= 0:
            return False
        
        return True
    
    # ============ MÉTODOS DE FÁBRICA ============
    
    @classmethod
    def crear_desde_datos_brutos(
        cls,
        nombre: str,
        precio_venta: float,
        stock_actual: float,
        unidad_stock: str = 'kg'
    ):
        """
        Método de fábrica para crear producto desde datos simples.
        """
        return cls(
            nombre=nombre,
            precio_venta=Dinero(precio_venta),
            stock_actual=Cantidad(stock_actual, unidad_stock),
            costo_ultima_compra=Dinero.zero()
        )
    
    # ============ REPRESENTACIONES ============
    
    def __repr__(self):
        return (
            f"Producto(id={self.id}, nombre='{self.nombre}', "
            f"precio={self.precio_venta}, stock={self.stock_actual}, "
            f"tipo='{self.tipo}', activo={self.activo})"
        )
    
    def __str__(self):
        estado = "✅" if self.activo else "❌"
        return f"{estado} {self.nombre}: {self.precio_venta} - Stock: {self.stock_actual}"
    
    def to_dict(self):
        """Serialización para uso en APIs"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio_venta': self.precio_venta.monto,
            'stock_actual': self.stock_actual.valor,
            'unidad_stock': self.stock_actual.unidad,
            'tipo': self.tipo,
            'activo': self.activo,
            'margen': self.calcular_margen()
        }