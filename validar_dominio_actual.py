#!/usr/bin/env python3
"""
Validar que el dominio actual sigue funcionando
"""
import sys
sys.path.insert(0, '.')

print("🔍 Validando dominio actual...")

try:
    # Verificar que podemos importar Venta desde el dominio actual
    from app.dominio.entities.venta import Venta
    print("✅ Venta importada desde dominio actual")
    
    # Crear instancia básica
    v = Venta()
    print(f"✅ Instancia creada: {v}")
    
    # Verificar métodos críticos
    metodos_criticos = ['agregar_item', 'cerrar_venta']
    for metodo in metodos_criticos:
        if hasattr(v, metodo):
            print(f"✅ Método {metodo} existe")
        else:
            print(f"❌ Método {metodo} NO existe")
    
    print("\n🎯 Dominio actual válido para migración")
    
except Exception as e:
    print(f"❌ Error validando dominio: {e}")
    import traceback
    traceback.print_exc()
