#!/bin/bash
# scripts/iniciar_web.sh

echo "🌐 INICIANDO DASHBOARD WEB..."
echo "================================================="

# Activar entorno
source ../venv/bin/activate

# Verificar estructura
if [ ! -f "../web/app.py" ]; then
    echo "❌ Error: No se encuentra web/app.py"
    exit 1
fi

# Iniciar servidor
echo "📊 Dashboard:    http://localhost:5000"
echo "💰 Caja:         http://localhost:5000/caja"
echo "🛒 Ventas:       http://localhost:5000/ventas"
echo "📈 Reportes:     http://localhost:5000/reportes"
echo "================================================="
echo "Presiona Ctrl+C para detener"
echo ""

cd ../web
python app.py