#!/bin/bash
# scripts/iniciar_cli.sh - VERSIÓN DEFINITIVA
echo "💻 INICIANDO DASHBOARD CLI..."
echo "================================================="

# 1. Ir a la raíz del proyecto (desde scripts/)
cd "$(dirname "$0")/.."
echo "📁 Directorio: $(pwd)"

# 2. Activar entorno virtual
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Entorno virtual activado"
else
    echo "⚠️  No hay entorno virtual, usando Python del sistema"
fi

# 3. Verificar archivos
if [ ! -f "app/run_dashboard.py" ]; then
    echo "❌ ERROR: No se encuentra app/run_dashboard.py"
    echo "Creando uno básico..."
    cat > app/run_dashboard.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.dashboard import DashboardCarniceria
    print("=" * 60)
    print("🥩 CARNE FELIZ - DASHBOARD CLI")
    print("=" * 60)
    dashboard = DashboardCarniceria()
    dashboard.ejecutar()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
EOF
fi

# 4. Verificar dashboard.py
if [ ! -f "app/dashboard.py" ]; then
    echo "❌ ERROR: No se encuentra app/dashboard.py"
    exit 1
fi

echo "✅ Archivos verificados"

# 5. Instalar dependencias si falta 'rich'
python -c "import rich" 2>/dev/null || {
    echo "📦 Instalando rich para interfaz mejorada..."
    pip install rich
}

# 6. Ejecutar
echo ""
echo "🚀 EJECUTANDO DASHBOARD..."
echo "================================================="
python app/run_dashboard.py