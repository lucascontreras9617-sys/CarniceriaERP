#!/bin/bash

echo "=========================================="
echo "🚀 CARNE FELIZ - SISTEMA DE GESTIÓN"
echo "=========================================="

# Obtener ruta absoluta del proyecto
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "📁 Directorio del proyecto: $PROJECT_DIR"

# Verificar estructura mínima
echo "🔍 Verificando estructura del proyecto..."
if [ ! -d "$PROJECT_DIR/web" ]; then
    echo "❌ ERROR: No se encuentra la carpeta 'web/'"
    exit 1
fi

if [ ! -d "$PROJECT_DIR/app" ]; then
    echo "❌ ERROR: No se encuentra la carpeta 'app/'"
    exit 1
fi

# Verificar Python
echo "🐍 Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✅ Python3 encontrado"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✅ Python encontrado"
else
    echo "❌ ERROR: Python no está instalado"
    exit 1
fi

# Verificar entorno virtual
echo "🔧 Verificando entorno virtual..."
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "✅ Entorno virtual encontrado"
    # Activar entorno virtual
    source "$PROJECT_DIR/venv/bin/activate"
    echo "✅ Entorno virtual activado"
else
    echo "⚠️  No se encontró entorno virtual. Usando Python global."
fi

# Verificar base de datos
echo "🗄️  Verificando base de datos..."
if [ ! -d "$PROJECT_DIR/data" ]; then
    echo "📁 Creando carpeta data/"
    mkdir -p "$PROJECT_DIR/data"
fi

# Verificar backend
echo "🔌 Verificando backend..."
cd "$PROJECT_DIR"

# Intentar importar backend_api
$PYTHON_CMD -c "
import sys
sys.path.insert(0, '.')
try:
    from app.backend_api import backend
    print('✅ Backend API disponible')
    estado = backend.sistema_listo()
    print(f'📊 Estado del sistema: {estado.get(\"estado\", \"DESCONOCIDO\")}')
except ImportError as e:
    print(f'⚠️  Backend API no disponible: {e}')
    print('⚠️  Usando modo simulación para desarrollo')
except Exception as e:
    print(f'⚠️  Error verificando backend: {e}')
    print('⚠️  Usando modo simulación para desarrollo')
"

# Verificar archivos HTML
echo "📄 Verificando templates web..."
if [ ! -f "$PROJECT_DIR/web/templates/dashboard.html" ]; then
    echo "⚠️  Advertencia: No se encontró dashboard.html"
fi

# Iniciar servidor web
echo ""
echo "=========================================="
echo "🌐 INICIANDO SERVIDOR WEB"
echo "=========================================="
echo "📱 URLs de acceso:"
echo "   • En ESTA computadora: http://localhost:5000"
echo "   • En la RED local: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "📋 Para detener el servidor: Presiona Ctrl+C"
echo "=========================================="

# Cambiar a carpeta web y ejecutar
cd "$PROJECT_DIR/web"
$PYTHON_CMD app.py
