#!/usr/bin/env python3
"""
Test LOCAL para verificar que Venta funciona
Ejecutar desde: /home/lucas/Escritorio/carniceria_erp/
"""
import sys
import os

print("🧪 TEST LOCAL - Ejecutando desde:", os.getcwd())
print("=" * 70)

# Agregar el directorio actual a sys.path
sys.path.insert(0, os.getcwd())

try:
    print("1. Intentando import absoluto...")
    import app.dominio
    print("   ✅ Módulo app.dominio importado")
    
    print("\n2. Verificando contenido del módulo...")
    print(f"   ¿Tiene atributo 'Venta'? {hasattr(app.dominio, 'Venta')}")
    
    if hasattr(app.dominio, 'Venta'):
        print("   ✅ app.dominio.Venta existe")
        Venta = app.dominio.Venta
    else:
        print("   ❌ app.dominio no tiene Venta")
        print("\n   Contenido de app.dominio:")
        for attr in dir(app.dominio):
            if not attr.startswith('_'):
                print(f"   - {attr}")
        
        # Intentar import directo
        print("\n3. Intentando import directo...")
        from app.dominio.entities.venta import Venta
        print("   ✅ from app.dominio.entities.venta import Venta funciona")
    
    # 4. Crear instancia
    print("\n4. Creando instancia de Venta...")
    venta = Venta()
    print(f"   ✅ Venta creada: {venta}")
    
    # 5. Verificar métodos
    print("\n5. Verificando métodos críticos...")
    print(f"   ¿Tiene agregar_item? {hasattr(venta, 'agregar_item')}")
    print(f"   ¿Tiene cerrar_venta? {hasattr(venta, 'cerrar_venta')}")
    
    # 6. Probar agregar_item
    print("\n6. Probando agregar_item()...")
    
    class MockProducto:
        def __init__(self, nombre):
            self.nombre = nombre
            self.stock_actual = type('obj', (object,), {'valor': 100.0})()
        
        def reducir_stock(self, cantidad):
            print(f"      [Mock] Stock reducido: {self.nombre}")
    
    producto = MockProducto("Bife de Chorizo")
    
    try:
        item = venta.agregar_item(producto, 5.0, 16.00)
        print(f"   ✅ agregar_item() FUNCIONÓ!")
        print(f"      Subtototal: ${item.get('subtotal', 'N/A')}")
    except Exception as e:
        print(f"   ❌ agregar_item() falló: {type(e).__name__}: {e}")
        # Mostrar traceback para debug
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 Si llegaste aquí, Venta funciona correctamente")
    
except ImportError as e:
    print(f"\n❌ IMPORT ERROR: {e}")
    print("\n🔍 Debug avanzado:")
    
    # Verificar sys.path
    print("\nsys.path:")
    for i, path in enumerate(sys.path[:10]):
        print(f"  {i}: {path}")
    
    # Verificar si app es un paquete
    app_path = os.path.join(os.getcwd(), 'app')
    print(f"\n¿Existe app/__init__.py? {os.path.exists(os.path.join(app_path, '__init__.py'))}")
    
    # Listar contenido de app
    print("\nContenido de app/:")
    for item in os.listdir(app_path):
        if os.path.isdir(os.path.join(app_path, item)):
            print(f"  📂 {item}/")
        elif item.endswith('.py'):
            print(f"  📄 {item}")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
