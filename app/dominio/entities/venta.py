"""
Venta - Entidad del Dominio con lógica de negocio
"""
from datetime import datetime
from uuid import uuid4
from decimal import Decimal
from typing import List, Optional

class ItemVenta:
    def __init__(self, producto, cantidad: float, precio_unitario: Decimal):
        self.id = str(uuid4())[:8]
        self.producto = producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.subtotal = Decimal(str(cantidad)) * precio_unitario
    
    def __repr__(self):
        return f"ItemVenta({self.producto.nombre}: {self.cantidad}kg × ${self.precio_unitario:.2f})"

class Venta:
    def __init__(self, cliente=None, empleado=None, tipo_pago='CONTADO'):
        self.id = str(uuid4())[:8]
        self.cliente = cliente
        self.empleado = empleado
        self.tipo_pago = tipo_pago
        self.fecha = datetime.now()
        self.items: List[ItemVenta] = []
        self.total = Decimal('0.00')
        self.estado = 'ABIERTA'
        self.comision_calculada = False
        
    def agregar_item(self, producto, cantidad: float, precio_unitario: float):
        """Agrega un item a la venta con validación de stock"""
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva")
        
        if producto.stock_actual < cantidad:
            raise ValueError(f"Stock insuficiente. Disponible: {producto.stock_actual}kg")
        
        # Convertir precio a Decimal
        precio_decimal = Decimal(str(precio_unitario))
        
        # Crear item
        item = ItemVenta(producto, cantidad, precio_decimal)
        self.items.append(item)
        
        # Actualizar total
        self.total += item.subtotal
        
        # Actualizar stock (simulado por ahora)
        # En una implementación real, esto se haría al cerrar la venta
        producto.stock_actual -= cantidad
        
        print(f"✅ Item agregado: {producto.nombre} ({cantidad}kg × ${precio_unitario:.2f})")
        return item
    
    def cerrar_venta(self):
        """Cierra la venta y aplica lógica de negocio"""
        if self.estado == 'CERRADA':
            raise ValueError("La venta ya está cerrada")
        
        if not self.items:
            raise ValueError("No se puede cerrar una venta sin items")
        
        # Calcular comisión para el empleado si aplica
        if self.empleado and not self.comision_calculada:
            comision = self.total * Decimal(str(self.empleado.comision_pct))
            print(f"💰 Comisión calculada para {self.empleado.nombre}: ${comision:.2f}")
            self.comision_calculada = True
        
        # Actualizar estado
        self.estado = 'CERRADA'
        self.fecha_cierre = datetime.now()
        
        print(f"✅ Venta {self.id} cerrada - Total: ${self.total:.2f}")
        print(f"   Cliente: {self.cliente.nombre if self.cliente else 'Sin cliente'}")
        print(f"   Items: {len(self.items)}")
        print(f"   Estado: {self.estado}")
    
    def __repr__(self):
        return f"Venta({self.id}: ${self.total:.2f} - {self.estado})"
