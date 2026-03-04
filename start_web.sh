#!/bin/bash
cd "$(dirname "$0")"

echo "=========================================="
echo "🌐 CARNE FELIZ - INTERFAZ WEB"
echo "=========================================="

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "🐍 Activando entorno virtual..."
    source venv/bin/activate
fi

# Instalar dependencias si faltan
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Instalando Flask..."
    pip install flask flask-cors
fi

echo ""
echo "🚀 Iniciando servidor web..."
echo ""
echo "📱 ACCESO DESDE CELULAR Y PC:"
echo "   • En ESTE equipo: http://localhost:5000"
echo "   • En la RED local: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "📝 Para salir: Ctrl+C"
echo "=========================================="
echo ""

# Ejecutar servidor web
cd web
python app.py
