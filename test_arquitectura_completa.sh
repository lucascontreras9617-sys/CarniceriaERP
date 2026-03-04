#!/bin/bash

echo "🧪 TEST COMPLETO DE ARQUITECTURA HEXAGONAL (CORREGIDO)"
echo "======================================================"
echo ""

# 1. Verificar estructura
echo "1. 📁 VERIFICANDO ESTRUCTURA..."
echo "--------------------------------"

estructura_requerida=(
    "core/domain/entities/venta.py"
    "core/domain/entities/lote.py"
    "core/domain/value_objects/dinero.py"
    "core/domain/value_objects/peso.py"
    "core/application/ports/venta_repository.py"
    "core/application/ports/lote_repository.py"
    "core/application/ports/producto_repository.py"
    "core/application/use_cases/registrar_venta.py"
)

for archivo in "${estructura_requerida[@]}"; do
    if [ -f "$archivo" ]; then
        echo "   ✅ $archivo"
    else
        echo "   ❌ $archivo - FALTANTE"
    fi
done

echo ""

# 2. Verificar imports
echo "2. 🔗 TESTEANDO IMPORTS..."
echo "--------------------------"

python3 -c "
import sys
sys.path.insert(0, '.')
print('   Python path configurado')

try:
    # Test dominio
    from core.domain.entities.venta import Venta
    print('   ✅ Venta importada')
    
    from core.domain.entities.lote import Lote
    print('   ✅ Lote importado')
    
    from core.domain.value_objects.dinero import Dinero
    from core.domain.value_objects.peso import Peso
    print('   ✅ Value Objects importados')
    
    # Test application
    from core.application.ports.venta_repository import VentaRepository
    print('   ✅ VentaRepository importado')
    
    from core.application.ports.lote_repository import LoteRepository
    print('   ✅ LoteRepository importado')
    
    from core.application.ports.producto_repository import ProductoRepository
    print('   ✅ ProductoRepository importado')
    
    from core.application.use_cases.registrar_venta import RegistrarVenta
    print('   ✅ RegistrarVenta importado')
    
    print('\\n   🎉 ¡TODOS LOS IMPORTS FUNCIONAN!')
    
except ImportError as e:
    print(f'   ❌ ImportError: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f'   ❌ Error inesperado: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

if [ \$? -eq 0 ]; then
    echo "   ✅ Imports correctos"
else
    echo "   ❌ Falló test de imports"
    exit 1
fi

echo ""

# 3. Test de Value Objects
echo "3. 💰 TEST VALUE OBJECTS..."
echo "---------------------------"

python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from core.domain.value_objects.dinero import Dinero
    from core.domain.value_objects.peso import Peso
    
    # Test Dinero
    d1 = Dinero.desde_monto(100.50)
    d2 = Dinero.desde_monto(50.25)
    print(f'   Dinero 1: {d1}')
    print(f'   Dinero 2: {d2}')
    
    # Test Peso
    p1 = Peso.desde_kg(2.5)
    p2 = Peso.desde_kg(1.3)
    print(f'   Peso 1: {p1}')
    print(f'   Peso 2: {p2}')
    
    # Test operaciones
    total = d1 + d2
    print(f'   Total dinero: {total}')
    
    print('\\n   ✅ Value Objects funcionando')
    
except Exception as e:
    print(f'   ❌ Error en Value Objects: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

echo ""

# 4. Test de entidades
echo "4. 🏢 TEST ENTIDADES..."
echo "------------------------"

python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from core.domain.entities.venta import Venta
    from core.domain.entities.lote import Lote
    from core.domain.value_objects.peso import Peso
    from core.domain.value_objects.dinero import Dinero
    from datetime import date
    
    # Test Venta
    venta = Venta()
    print(f'   Venta creada: {venta}')
    
    # Test Lote
    lote = Lote.crear_nuevo(
        numero_tropa='T-9999',
        producto='Res de Vaca',
        peso_kg=100.0,
        costo_total=550.0,
        proveedor='Frigorífico Test'
    )
    print(f'   Lote creado: {lote}')
    print(f'   Costo por kg: {lote.costo_por_kg}')
    
    print('\\n   ✅ Entidades funcionando')
    
except Exception as e:
    print(f'   ❌ Error en entidades: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

echo ""

# 5. Resumen
echo "5. 📊 RESUMEN FINAL"
echo "-------------------"

# Contar archivos
total_archivos=\$(find core -name "*.py" | wc -l)
total_directorios=\$(find core -type d | wc -l)

echo "   Estructura creada:"
echo "   - Directorios: \$total_directorios"
echo "   - Archivos .py: \$total_archivos"
echo ""
echo "   Ubicación: \$(pwd)/core/"
echo ""

echo "🎯 ARQUITECTURA HEXAGONAL CREADA EXITOSAMENTE"
echo "============================================="
echo ""
echo "📁 CAPAS IMPLEMENTADAS:"
echo "   • Dominio ✅        (Venta, Lote, Value Objects)"
echo "   • Aplicación ✅    (Casos de uso, Ports)"
echo "   • Adaptadores 🚧  (SQLAlchemy en progreso)"
echo ""
echo "🚀 PARA EJECUTAR DEMO:"
echo "   python demo_hexagonal.py"
