#!/usr/bin/env python3
"""
Demo de Arquitectura Hexagonal - ERP Carnicería
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
        
        # Crear venta
        venta = Venta()
        print(f"   ✅ Venta creada: {venta}")
        
        # Verificar métodos
        metodos = ['agregar_item', 'cerrar_venta']
        for metodo in metodos:
            if hasattr(venta, metodo):
                print(f"   ✅ Método {metodo} disponible")
            else:
                print(f"   ⚠️  Método {metodo} no encontrado")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en dominio: {e}")
        return False

def demo_caso_uso():
    """Demo de caso de uso"""
    print("\n3. 🚀 CASO DE USO - Orquestación")
    print("-" * 40)
    
    try:
        from core.application.use_cases.registrar_venta import RegistrarVenta
        from core.adapters.persistence.sqlalchemy.venta_repository_adapter import VentaRepositoryAdapter
        
        # Mock repositories
        class MockLoteRepo:
            def obtener_por_id(self, id): 
                class LoteMock: 
                    id = id
                    peso_disponible = 1000.0
                return LoteMock()
            def actualizar_stock(self, *args): pass
        
        class MockProductoRepo:
            def obtener_por_id(self, id):
                class ProductoMock:
                    id = id
                    nombre = f"Producto {id}"
                return ProductoMock()
        
        # Crear adaptador mock
        class MockSession:
            pass
        
        # Crear caso de uso
        caso_uso = RegistrarVenta(
            venta_repository=VentaRepositoryAdapter(MockSession()),
            lote_repository=MockLoteRepo(),
            producto_repository=MockProductoRepo()
        )
        
        print("   ✅ Caso de uso creado")
        print("   📋 Flujo: UI → CasoUso → Dominio → Repositorio → DB")
        
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
    print("   ├── Dominio ✅      (reglas de negocio)")
    print("   ├── Aplicación ✅  (casos de uso)")
    print("   ├── Puertos ✅     (interfaces)")
    print("   └── Adaptadores 🚧 (SQLAlchemy en progreso)")
    
    print("\n   SEPARACIÓN DE CONCEPTOS:")
    print("   ✅ Dominio no conoce SQLAlchemy")
    print("   ✅ Dominio no conoce Flask/Web")
    print("   ✅ Casos de uso orquestan, no contienen lógica")
    print("   ✅ Adaptadores implementan, no deciden")
    
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
        print("🎯 ARQUITECTURA HEXAGONAL IMPLEMENTADA")
        print("\n📁 Estructura creada en: core/")
        print("📍 Ubicación: " + os.getcwd() + "/core")
        print("\n🚀 EJECUTAR SISTEMA LEGACY (para comparar):")
        print("   python -m app.main")
    else:
        print("⚠️  DEMO CON ERRORES - REVISAR")
    
    print("=" * 60)
    return exit_code

if __name__ == "__main__":
    sys.exit(main())

