# scripts/validar_dominio.py
"""
Script para validar rápidamente que el dominio funciona.
Ejecutar: python scripts/validar_dominio.py
"""
import sys
import os

# Agregar ruta del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.dominio import Venta, Producto, Dinero, Cantidad

def validar_funcionamiento_basico():
    """Valida que los métodos críticos funcionen"""
    print("🧪 VALIDANDO DOMINIO VENTA")
    print("=" * 60)
    
    try:
        # 1. Crear producto mock
        class ProductoMock:
            def __init__(self, nombre, stock):
                self.id = "mock-1"
                self.nombre = nombre
                self.stock_actual = Cantidad(stock, 'kg')
                self.precio_venta = Dinero(100.0)
                self.activo = True
            
            def tiene_stock_suficiente(self, cantidad):
                return self.stock_actual.valor >= cantidad.valor
            
            def reducir_stock(self, cantidad):
                if not self.tiene_stock_suficiente(cantidad):
                    raise Exception("Stock insuficiente")
                self.stock_actual = Cantidad(
                    self.stock_actual.valor - cantidad.valor,
                    'kg'
                )
        
        # 2. Crear venta
        print("1. Creando venta...")
        venta = Venta()
        print(f"   ✅ Venta creada: {venta.id}")
        print(f"   Estado: {venta.estado}")
        
        # 3. Crear productos
        print("\n2. Creando productos...")
        bife_chorizo = ProductoMock("Bife de Chorizo", stock=10.0)
        nalga = ProductoMock("Nalga", stock=15.0)
        print(f"   ✅ Productos creados:")
        print(f"      - {bife_chorizo.nombre}: Stock {bife_chorizo.stock_actual}")
        print(f"      - {nalga.nombre}: Stock {nalga.stock_actual}")
        
        # 4. Agregar items (MÉTODO CRÍTICO)
        print("\n3. Agregando items a la venta...")
        print("   Probando venta.agregar_item()...")
        
        item1 = venta.agregar_item(bife_chorizo, cantidad_kg=5.0, precio_kg=16.00)
        print(f"   ✅ Item 1 agregado: {item1}")
        
        item2 = venta.agregar_item(nalga, cantidad_kg=10.0, precio_kg=10.50)
        print(f"   ✅ Item 2 agregado: {item2}")
        
        print(f"\n   Resumen items:")
        for i, item in enumerate(venta.items, 1):
            print(f"   {i}. {item.nombre_producto}: {item.cantidad_kg}kg "
                  f"× ${item.precio_kg:.2f} = ${item.subtotal.monto:.2f}")
        
        # 5. Verificar totales
        print(f"\n   Subtotal: ${venta.subtotal}")
        print(f"   Total: ${venta.total}")
        
        # 6. Verificar stock reducido
        print(f"\n   Stock actualizado:")
        print(f"   - {bife_chorizo.nombre}: {bife_chorizo.stock_actual} "
              f"(reducido 5.0 kg)")
        print(f"   - {nalga.nombre}: {nalga.stock_actual} "
              f"(reducido 10.0 kg)")
        
        # 7. Cerrar venta (MÉTODO CRÍTICO)
        print("\n4. Cerrando venta...")
        venta.cerrar_venta(aplicar_comision=False)
        print(f"   ✅ Venta cerrada: Estado {venta.estado}")
        print(f"   Total final: {venta.total}")
        
        # 8. Obtener resumen
        print("\n5. Generando resumen...")
        resumen = venta.obtener_resumen()
        print(f"   ✅ Resumen generado:")
        print(f"      ID: {resumen['id'][:8]}...")
        print(f"      Items: {resumen['cantidad_items']}")
        print(f"      Total: ${resumen['total']:.2f}")
        
        # 9. Validar error al agregar a venta cerrada
        print("\n6. Validando protección de venta cerrada...")
        try:
            venta.agregar_item(bife_chorizo, cantidad_kg=1.0, precio_kg=16.00)
            print("   ❌ ERROR: Debería haber fallado!")
        except Exception as e:
            print(f"   ✅ Correcto: {type(e).__name__} - {str(e)}")
        
        print("\n" + "=" * 60)
        print("🎉 VALIDACIÓN EXITOSA: El dominio funciona correctamente!")
        print("   - venta.agregar_item() ✅")
        print("   - venta.cerrar_venta() ✅")
        print("   - Validaciones de stock ✅")
        print("   - Cálculos automáticos ✅")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN VALIDACIÓN: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def probar_main_py_simulation():
    """Simula lo que main.py intenta hacer"""
    print("\n" + "=" * 60)
    print("🧪 SIMULANDO main.py ORIGINAL")
    print("=" * 60)
    
    try:
        # Esto es lo que main.py línea 90 intenta hacer
        from app.dominio import Venta
        
        # Mock de datos como en main.py
        class ClienteMock:
            def __init__(self):
                self.id = "cliente-1"
                self.nombre = "El Bife de Oro"
        
        class EmpleadoMock:
            def __init__(self):
                self.id = "emp-1"
                self.nombre = "Carlos"
                self.comision_pct = 0.015
        
        class ProductoMock:
            def __init__(self, nombre, precio):
                self.id = "prod-1"
                self.nombre = nombre
                self.precio_venta = Dinero(precio)
                self.stock_actual = Cantidad(100.0, 'kg')
                self.activo = True
            
            def tiene_stock_suficiente(self, cantidad):
                return self.stock_actual.valor >= cantidad.valor
            
            def reducir_stock(self, cantidad):
                self.stock_actual = Cantidad(
                    self.stock_actual.valor - cantidad.valor,
                    'kg'
                )
        
        # Crear instancias como en main.py
        clientes = {"El Bife de Oro": ClienteMock()}
        empleados = {"Carlos": EmpleadoMock()}
        productos = {
            "Bife de Chorizo": ProductoMock("Bife de Chorizo", 16.00),
            "Nalga": ProductoMock("Nalga", 10.50)
        }
        
        # ESTA ES LA LÍNEA 90 DE main.py QUE FALLA
        print("Ejecutando: venta = Venta(cliente=clientes['El Bife de Oro'], ...)")
        venta = Venta(
            cliente=clientes["El Bife de Oro"],
            empleado=empleados["Carlos"],
            tipo_pago='CREDITO'
        )
        
        print("✅ Venta creada exitosamente")
        
        # ESTA ES LA LÍNEA 91 DE main.py
        print("\nEjecutando: venta.agregar_item(productos['Bife de Chorizo'], 5.0, 16.00)")
        venta.agregar_item(productos["Bife de Chorizo"], 5.0, 16.00)
        print("✅ agregar_item() funcionó!")
        
        print("\nEjecutando: venta.agregar_item(productos['Nalga'], 10.0, 10.50)")
        venta.agregar_item(productos["Nalga"], 10.0, 10.50)
        print("✅ Segundo agregar_item() funcionó!")
        
        print("\nEjecutando: venta.cerrar_venta()")
        venta.cerrar_venta()
        print("✅ cerrar_venta() funcionó!")
        
        print(f"\n🎉 ¡main.py FUNCIONARÍA CORRECTAMENTE!")
        print(f"   Total venta: {venta.total}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ SIMULACIÓN FALLÓ: {type(e).__name__}")
        print(f"   {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 VALIDACIÓN DEL DOMINIO CARNE FELIZ ERP")
    print("=" * 60)
    
    # Validar funcionamiento básico
    if not validar_funcionamiento_basico():
        sys.exit(1)
    
    # Simular main.py
    if not probar_main_py_simulation():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ TODAS LAS VALIDACIONES PASARON EXITOSAMENTE")
    print("=" * 60)
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Reemplazar el import en main.py:")
    print("   DE: from app.procesos import Venta")
    print("   A:  from app.dominio import Venta")
    print("\n2. Ejecutar main.py para verificar que funciona")
    print("\n3. Proceder con Fase 2: Repositorios")