#!/bin/bash
cd "$(dirname "$0")"
echo "🚀 Iniciando Dashboard Carnicería..."
echo "📁 Directorio: $(pwd)"
echo "🐍 Python: $(python3 --version)"

# Verificar archivos
if [ ! -f "app/dashboard.py" ]; then
    echo "❌ Error: No se encuentra app/dashboard.py"
    exit 1
fi

if [ ! -f "app/caja.py" ]; then
    echo "❌ Error: No se encuentra app/caja.py"
    exit 1
fi

# Ejecutar
python3 run_dashboard.py
