#!/bin/bash
# scripts/iniciar_sistema.sh - SCRIPT UNIFICADO

echo "================================================="
echo "🥩 CARNE FELIZ - ERP UNIFICADO"
echo "================================================="
echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado. Instale Python 3.8+"
    exit 1
fi
echo "✓ Python: $(python3 --version)"

# 2. Activar entorno virtual
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Entorno virtual activado"
else
    echo "🔄 Creando entorno virtual..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 3. Instalar dependencias
echo "📦 Instalando dependencias..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Crear requirements básico
    cat > requirements.txt << EOF
flask>=2.3.0
sqlalchemy>=2.0.0
pandas>=2.0.0
openpyxl>=3.1.0
rich>=13.0.0
EOF
    pip install -r requirements.txt
fi
echo "✓ Dependencias instaladas"

# 4. Verificar/crear estructura
echo "📁 Verificando estructura..."
mkdir -p data web/static web/templates app scripts

# 5. Inicializar base de datos
echo "🗄️  Inicializando base de datos..."
python3 -c "
import sys
sys.path.append('.')
from app.persistencia import db_manager
from app.modelos import Base
print('✅ Base de datos SQLAlchemy lista')
"

# 6. Verificar estado del sistema
echo "🔍 Verificando estado del sistema..."
python3 -c "
import sys
sys.path.append('.')
from app.caja import ControlCaja
from app.dashboard_data import DashboardData

estado = ControlCaja.obtener_estado_caja()
if estado['existe']:
    print(f'✅ Caja: {estado[\"estado\"].upper()}')
    if estado['estado'] == 'abierta':
        print(f'   Responsable: {estado[\"responsable\"]}')
        print(f'   Monto: \${estado[\"monto_inicial\"]:.2f}')
else:
    print('ℹ️  No hay caja abierta hoy')

# Alertas iniciales
datos = DashboardData.obtener_dashboard_principal()
if datos['success']:
    alertas = datos['total_alertas']
    if alertas > 0:
        print(f'⚠️  {alertas} alertas pendientes')
    else:
        print('✅ Sin alertas críticas')
else:
    print(f'⚠️  Error en dashboard: {datos.get(\"error\")}')
"

echo ""
echo "🎯 SISTEMA LISTO"
echo "================================================="
echo "OPCIONES:"
echo "1. 🌐 Dashboard Web:   ./scripts/iniciar_web.sh"
echo "2. 💻 Terminal CLI:    ./scripts/iniciar_cli.sh"
echo "3. 📊 Ambos:           Ejecutar ambos scripts en terminales separadas"
echo "================================================="