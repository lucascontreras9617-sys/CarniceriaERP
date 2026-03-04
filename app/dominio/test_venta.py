# tests/dominio/test_venta.py
"""
Tests para la entidad Venta del dominio.
Ejecutar con: python -m pytest tests/dominio/test_venta.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
from app.dominio import Venta, Producto, Dinero, Cantidad
from app.dominio.exceptions import (
    VentaCerradaError, 
    VentaSinItemsError,
    StockInsuficienteError,
    ValorInvalidoError
)

class TestProductoMock:
    """Mock de Producto para testing"""
    def __init__(self, nombre, stock_inicial):
        self.id = "test-id"
        self.nombre = nombre
        self.stock_actual = Cantidad(stock_inicial, 'kg')
        self.precio_venta = Dinero(100.0)
        self.activo = True
    
    def tiene_stock_suficiente(self, cantidad):
        return self.stock_actual.valor >= cantidad.valor
    
    def reducir_stock(self, cantidad):
        if not self.tiene_stock_suficiente(cantidad):
            raise StockInsuficienteError("Stock insuficiente")
        self.stock_actual = Cantidad(
            self.stock_actual.valor - cantidad.valor,
            'kg'
        )

class TestClienteMock:
    def __init__(self, nombre):
        self.id = "cliente-test"
        self.nombre = nombre
        self.saldo_pendiente = Dinero.zero()
        self.total_compras = 0

class TestEmpleadoMock:
    def __init__(self, nombre):
        self.id = "empleado-test"
        self.nombre = nombre
        self.comision_pct = 0.05
        self.comision_acumulada = Dinero.zero()

class TestVenta:
    """Tests para la clase Venta"""
    
    def test_creacion_venta(self):
        """Test creación básica de venta"""
        venta = Venta()
        assert venta.estado == 'ABIERTA'
        assert len(venta.items) == 0
        assert venta.total.monto == 0.0
        assert venta.id is not None
    
    def test_agregar_item_valido(self):
        """Test agregar item con datos válidos"""
        # Arrange
        producto = TestProductoMock("Bife de Chorizo", stock_inicial=10.0)
        venta = Venta()
        
        # Act
        item = venta.agregar_item(producto, cantidad_kg=2.5, precio_kg=150.0)
        
        # Assert
        assert len(venta.items) == 1
        assert venta.items[0] == item
        assert item.cantidad_kg == 2.5
        assert item.precio_kg == 150.0
        assert item.subtotal.monto == 375.0  # 2.5 * 150
        assert venta.total.monto == 375.0
        assert producto.stock_actual.valor == 7.5  # 10 - 2.5
    
    def test_agregar_item_stock_insuficiente(self):
        """Test que falla al agregar item sin stock suficiente"""
        # Arrange
        producto = TestProductoMock("Producto Test", stock_inicial=1.0)
        venta = Venta()
        
        # Act & Assert
        with pytest.raises(StockInsuficienteError):
            venta.agregar_item(producto, cantidad_kg=2.0, precio_kg=100.0)
        
        # Verificar que no se agregó el item
        assert len(venta.items) == 0
        assert venta.total.monto == 0.0
    
    def test_agregar_item_cantidad_invalida(self):
        """Test con cantidad negativa o cero"""
        producto = TestProductoMock("Producto Test", stock_inicial=10.0)
        venta = Venta()
        
        with pytest.raises(ValorInvalidoError):
            venta.agregar_item(producto, cantidad_kg=0, precio_kg=100.0)
        
        with pytest.raises(ValorInvalidoError):
            venta.agregar_item(producto, cantidad_kg=-1, precio_kg=100.0)
    
    def test_agregar_item_precio_invalido(self):
        """Test con precio negativo o cero"""
        producto = TestProductoMock("Producto Test", stock_inicial=10.0)
        venta = Venta()
        
        with pytest.raises(ValorInvalidoError):
            venta.agregar_item(producto, cantidad_kg=1.0, precio_kg=0)
        
        with pytest.raises(ValorInvalidoError):
            venta.agregar_item(producto, cantidad_kg=1.0, precio_kg=-50.0)
    
    def test_agregar_item_venta_cerrada(self):
        """Test que no permite agregar items a venta cerrada"""
        # Arrange
        producto = TestProductoMock("Producto Test", stock_inicial=10.0)
        venta = Venta()
        venta.agregar_item(producto, cantidad_kg=1.0, precio_kg=100.0)
        venta.cerrar_venta()
        
        # Act & Assert
        with pytest.raises(VentaCerradaError):
            venta.agregar_item(producto, cantidad_kg=1.0, precio_kg=100.0)
    
    def test_cerrar_venta_valida(self):
        """Test cierre de venta con items"""
        # Arrange
        producto1 = TestProductoMock("Producto 1", stock_inicial=10.0)
        producto2 = TestProductoMock("Producto 2", stock_inicial=5.0)
        cliente = TestClienteMock("Cliente Test")
        empleado = TestEmpleadoMock("Empleado Test")
        
        venta = Venta(cliente=cliente, empleado=empleado)
        venta.agregar_item(producto1, cantidad_kg=2.0, precio_kg=100.0)
        venta.agregar_item(producto2, cantidad_kg=1.0, precio_kg=50.0)
        
        # Act
        venta_cerrada = venta.cerrar_venta()
        
        # Assert
        assert venta_cerrada.estado == 'CERRADA'
        assert venta_cerrada.fecha_cierre is not None
        assert venta_cerrada.total.monto == 250.0  # 200 + 50
        assert venta_cerrada.comision_empleado.monto == 12.5  # 5% de 250
    
    def test_cerrar_venta_sin_items(self):
        """Test que no permite cerrar venta sin items"""
        venta = Venta()
        
        with pytest.raises(VentaSinItemsError):
            venta.cerrar_venta()
    
    def test_venta_con_multiple_items(self):
        """Test venta con múltiples items y total correcto"""
        # Arrange
        productos = [
            TestProductoMock(f"Producto {i}", stock_inicial=20.0)
            for i in range(3)
        ]
        
        venta = Venta()
        
        # Act - Agregar múltiples items
        venta.agregar_item(productos[0], cantidad_kg=2.0, precio_kg=100.0)  # 200
        venta.agregar_item(productos[1], cantidad_kg=1.5, precio_kg=80.0)   # 120
        venta.agregar_item(productos[2], cantidad_kg=3.0, precio_kg=60.0)   # 180
        
        # Assert
        assert len(venta.items) == 3
        assert venta.total.monto == 500.0  # 200 + 120 + 180
        
        # Verificar stock reducido
        assert productos[0].stock_actual.valor == 18.0  # 20 - 2
        assert productos[1].stock_actual.valor == 18.5  # 20 - 1.5
        assert productos[2].stock_actual.valor == 17.0  # 20 - 3
    
    def test_resumen_venta(self):
        """Test que genera resumen correcto"""
        # Arrange
        cliente = TestClienteMock("Juan Pérez")
        empleado = TestEmpleadoMock("Carlos Gómez")
        producto = TestProductoMock("Vacio", stock_inicial=15.0)
        
        venta = Venta(
            cliente=cliente,
            empleado=empleado,
            tipo_pago='EFECTIVO'
        )
        
        venta.agregar_item(producto, cantidad_kg=2.5, precio_kg=120.0)
        venta.cerrar_venta()
        
        # Act
        resumen = venta.obtener_resumen()
        
        # Assert
        assert resumen['id'] == venta.id
        assert resumen['cliente'] == 'Juan Pérez'
        assert resumen['empleado'] == 'Carlos Gómez'
        assert resumen['tipo_pago'] == 'EFECTIVO'
        assert resumen['estado'] == 'CERRADA'
        assert resumen['cantidad_items'] == 1
        assert resumen['total'] == 300.0  # 2.5 * 120
        assert len(resumen['items']) == 1
        assert resumen['items'][0]['producto_nombre'] == 'Vacio'
    
    def test_venta_credito_aumenta_saldo_cliente(self):
        """Test que venta a crédito aumenta saldo pendiente del cliente"""
        # Arrange
        cliente = TestClienteMock("Cliente Crédito")
        producto = TestProductoMock("Producto", stock_inicial=10.0)
        
        venta = Venta(cliente=cliente, tipo_pago='CREDITO')
        venta.agregar_item(producto, cantidad_kg=2.0, precio_kg=100.0)
        
        # Act
        venta.cerrar_venta()
        
        # Assert
        assert cliente.saldo_pendiente.monto == 200.0
        assert cliente.total_compras == 1

if __name__ == '__main__':
    # Ejecutar tests manualmente
    pytest.main(['-v', __file__])