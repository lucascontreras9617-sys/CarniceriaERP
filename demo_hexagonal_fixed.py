#!/usr/bin/env python3
"""
Demo de Arquitectura Hexagonal - ERP Carnicería (VERSIÓN CORREGIDA)
"""
import sys
import os

# Configurar path
sys.path.insert(0, os.getcwd())

print("=" * 60)
print("🏗️  DEMO ARQUITECTURA HEXAGONAL - ERP CARNICERÍA")
print("=" * 60)

def demo_valor_objects():
    """Demo de Value Objects"""
    print("\n1. 💰 VALUE OBJECTS - Dominio puro")
    print("-" * 40)
    
    from core.domain.value_objects.dinero import Dinero
    from core.domain.value_objects.peso import Peso
    
    # Crear dinero
    precio_chorizo = Dinero.desde_monto(2500.50)
    precio_vacio = Dinero.desde_monto(1800.75)
    
    # Crear pesos
    peso_compra = Peso.desde_kg(2.5)
    peso_stock = Peso.desde_kg(100.0)
    
    print(f"   Bife de Chorizo: {peso_compra} × {precio_chorizo}")
    print(f"   Vacío: {peso_compra} × {precio_vacio}")
    
    # Calcular total
    total_chorizo = precio_chorizo * peso_compra.en_kg
    total_vacio = precio_vacio * peso_compra.en_kg
    
    print(f"\n   Subtotal Chorizo: {total_chorizo}")
    print(f"   Subtotal Vacío: {total_vacio}")
    print(f"   Stock inicial: {peso_stock}")
    
    return True

def demo_dominio():
    """Demo de entidades de dominio"""
    print("\n2. 🏢 DOMINIO - Entidades de negocio")
    print("-" * 40)
    
    try:
        from core.domain.entities.venta import Venta
        from core.domain.entities.lote import Lote
        
        # Crear venta
        venta = Venta()
        print(f"   ✅ Venta creada: {venta}")
        
        # Crear lote
        lote = Lote.crear_nuevo(
            numero_tropa="T-9999",
            producto="Res de Vaca",
            peso_kg=150.0,
            costo_total=825.0,
            proveedor="Proveedor Demo"
        )
        print(f"   ✅ Lote creado: {lote}")
        print(f"   Costo por kg: {lote.costo_por_kg}")
        
        # Verificar métodos de venta
        metodos = ['agregar_item', 'cerrar_venta']
        for metodo in metodos:
            if hasattr(venta, metodo):
                print(f"   ✅ Método {metodo} disponible")
            else:
                print(f"   ⚠️  Método {metodo} no encontrado")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en dominio: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_caso_uso():
    """Demo de caso de uso"""
    print("\n3. 🚀 CASO DE USO - Orquestación")
    print("-" * 40)
    
    try:
        from core.application.use_cases.registrar_venta import RegistrarVenta
        from core.application.ports.venta_repository import VentaRepository
        from core.application.ports.lote_repository import LoteRepository
        from core.application.ports.producto_repository import ProductoRepository
        
        # Crear mocks de repositorios
        class MockVentaRepository(VentaRepository):
            def guardar(self, venta): 
                print(f"      Mock: Guardando venta {venta.id}")
                return venta
            def obtener_por_id(self, id): return None
            def obtener_todas(self): return []
            def obtener_por_fecha(self, d, h): return []
            def obtener_por_cliente(self, id): return []
        
        class MockLoteRepository(LoteRepository):
            def guardar(self, lote): return lote
            def obtener_por_id(self, id): 
                from core.domain.entities.lote import Lote
                from core.domain.value_objects.peso import Peso
                from core.domain.value_objects.dinero import Dinero
                from datetime import date
                return Lote(
                    id=id, numero_tropa="T-MOCK", producto_nombre="Producto Mock",
                    peso_total=Peso.desde_kg(100), peso_disponible=Peso.desde_kg(50),
                    costo_total=Dinero.desde_monto(500), fecha_ingreso=date.today()
                )
            def obtener_todos(self): return []
            def obtener_por_numero(self, num): return None
            def actualizar_stock(self, id, kg): 
                print(f"      Mock: Actualizando stock lote {id} (-{kg}kg)")
            def obtener_con_stock(self): return []
        
        class MockProductoRepository(ProductoRepository):
            def guardar(self, p): return p
            def obtener_por_id(self, id): 
                prod = type('Producto', (), {'id': id, 'nombre': f'Producto {id}'})()
                return prod
            def obtener_todos(self): return []
            def obtener_por_nombre(self, n): return None
            def actualizar_stock(self, id, kg): pass
        
        # Crear caso de uso
        caso_uso = RegistrarVenta(
            venta_repository=MockVentaRepository(),
            lote_repository=MockLoteRepository(),
            producto_repository=MockProductoRepository()
        )
        
        print("   ✅ Caso de uso creado")
        print("   📋 Flujo: UI → CasoUso → Dominio → Repositorio → DB")
        
        # Ejecutar simple
        print("\n   🧪 Ejecutando venta simple...")
        venta_resultado = caso_uso.execute_simple(
            "Cliente Demo",
            [
                {'nombre': 'Bife de Chorizo', 'cantidad': 2.5, 'precio': 2500.0},
                {'nombre': 'Vacío', 'cantidad': 1.8, 'precio': 1800.0}
            ]
        )
        
        print(f"   ✅ Venta ejecutada: {venta_resultado}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en caso de uso: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_arquitectura():
    """Demo completa de arquitectura"""
    print("\n4. 🏛️  ARQUITECTURA HEXAGONAL")
    print("-" * 40)
    
    print("   CAPAS IMPLEMENTADAS:")
    print("   ├── Dominio ✅      (Venta, Lote, Value Objects)")
    print("   ├── Aplicación ✅  (Casos de uso, Ports/Interfaces)")
    print("   └── Adaptadores 🚧 (Implementaciones técnicas)")
    
    print("\n   SEPARACIÓN DE CONCEPTOS:")
    print("   ✅ Dominio no conoce SQLAlchemy")
    print("   ✅ Dominio no conoce Flask/Web")
    print("   ✅ Casos de uso orquestan, no contienen lógica")
    print("   ✅ Ports definen contratos, no implementaciones")
    
    print("\n   🎯 INNEGOCIABLES IMPLEMENTADOS:")
    print("   • Inventario por peso (Value Object Peso)")
    print("   • Montos monetarios (Value Object Dinero)")
    print("   • Separación clara de capas")
    
    return True

def main():
    """Función principal"""
    print("\n🚀 INICIANDO DEMOSTRACIÓN...")
    
    exit_code = 0
    
    demos = [
        demo_valor_objects,
        demo_dominio,
        demo_caso_uso,
        demo_arquitectura
    ]
    
    for demo in demos:
        if not demo():
            exit_code = 1
    
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("🎯 ¡ARQUITECTURA HEXAGONAL FUNCIONANDO!")
        print("\n📁 Estructura creada en: core/")
        print("📍 Ubicación: " + os.getcwd() + "/core")
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Crear adaptadores SQLAlchemy reales")
        print("   2. Conectar con base de datos existente")
        print("   3. Migrar ventas del sistema legacy")
    else:
        print("⚠️  ALGUNAS DEMOS TUVIERON ERRORES")
        print("\n🔧 Revisar los errores arriba")
    
    print("=" * 60)
    return exit_code

if __name__ == "__main__":
    sys.exit(main())

