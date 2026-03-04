#!/bin/bash
# iniciar_todo.sh - Inicia todo el sistema Carne Feliz ERP (Versión corregida)

echo "==============================================="
echo "🥩  INICIANDO SISTEMA CARNE FELIZ ERP v2.4.0"
echo "==============================================="

# Activar entorno virtual
if [ -d "venv" ]; then
    echo "🔧 Activando entorno virtual..."
    source venv/bin/activate
elif [ -d "web/venv" ]; then
    echo "🔧 Activando entorno virtual (web/venv)..."
    source web/venv/bin/activate
else
    echo "⚠️  No se encontró entorno virtual. Usando Python del sistema."
fi

# Verificar Python y dependencias
echo "🐍 Verificando Python..."
python3 --version

echo "📦 Verificando dependencias..."
pip list | grep -E "(Flask|Django|sqlite|requests)"

# Obtener IP local dinámicamente
echo "🌐 Detectando IP local..."
IP_LOCAL=$(python3 -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 53))
    ip = s.getsockname()[0]
    s.close()
    print(ip)
except:
    print('127.0.0.1')
")

echo "📡 IP Local: $IP_LOCAL"
echo "🔌 Puertos: Flask (5000), Django (5001)"
echo "🌐 URLs:"
echo "   • Flask Dashboard: http://$IP_LOCAL:5000"
echo "   • Django Reportes: http://$IP_LOCAL:5001/reportes"

echo ""
echo "¿Qué deseas iniciar?"
echo "1) Solo Flask Web (Dashboard) - Puerto 5000"
echo "2) Solo Django (Reportes) - Puerto 5001"
echo "3) Ambos (en terminales separadas) - Puertos 5000 y 5001"
echo "4) Verificar estado del sistema"
echo "5) Configurar puertos manualmente"
echo "6) Salir"
echo ""

read -p "Selección [1-6]: " opcion

case $opcion in
    1)
        echo "🚀 Iniciando Flask Dashboard..."
        echo "🌐 URL: http://$IP_LOCAL:5000"
        cd web
        python app.py
        ;;
    2)
        echo "📊 Iniciando Django Reportes..."
        echo "🌐 URL: http://$IP_LOCAL:5001"
        cd django_report
        python manage.py runserver $IP_LOCAL:5001
        ;;
    3)
        echo "⚡ Iniciando ambos servicios..."
        echo "📡 Usando puertos diferentes para evitar conflicto:"
        echo "   • Flask: http://$IP_LOCAL:5000"
        echo "   • Django: http://$IP_LOCAL:5001"
        echo ""
        
        # Opción 1: Usar screen/tmux si están disponibles
        if command -v screen &> /dev/null; then
            echo "🖥️  Usando screen para múltiples terminales..."
            
            # Crear sesión de screen
            screen -S carniceria -dm bash -c "cd $(pwd)/django_report && python manage.py runserver $IP_LOCAL:5001; exec bash"
            echo "✅ Django iniciado en segundo plano (screen)"
            
            # Iniciar Flask en primer plano
            echo "🚀 Iniciando Flask en esta terminal..."
            cd web
            python app.py
            
        # Opción 2: Usar gnome-terminal
        elif command -v gnome-terminal &> /dev/null; then
            echo "🖥️  Abriendo nueva terminal para Django..."
            gnome-terminal -- bash -c "cd $(pwd)/django_report && python manage.py runserver $IP_LOCAL:5001; exec bash"
            sleep 2
            
            echo "🚀 Iniciando Flask en esta terminal..."
            cd web
            python app.py
            
        # Opción 3: Instrucciones manuales
        else
            echo "⚠️  No se encontró screen ni gnome-terminal."
            echo ""
            echo "Para iniciar ambos servicios, abre DOS terminales:"
            echo ""
            echo "TERMINAL 1 (Django):"
            echo "  cd $(pwd)/django_report"
            echo "  python manage.py runserver $IP_LOCAL:5001"
            echo ""
            echo "TERMINAL 2 (Flask):"
            echo "  cd $(pwd)/web"
            echo "  python app.py"
            echo ""
            echo "Presiona Enter para intentar iniciar Flask en esta terminal..."
            read
            
            echo "🚀 Iniciando Flask..."
            cd web
            python app.py
        fi
        ;;
    4)
        echo "🔍 Verificando estado del sistema..."
        echo ""
        echo "📁 Estructura de directorios:"
        ls -la
        echo ""
        echo "🌐 Configuración de red:"
        ip addr show | grep inet | grep -v 127.0.0.1 | grep -v inet6
        echo ""
        echo "🔌 Puertos en uso:"
        netstat -tulpn | grep :500 || echo "  (Puertos 5000-5001 libres)"
        echo ""
        echo "📦 Dependencias instaladas:"
        pip list | grep -E "(Flask|Django|requests)"
        ;;
    5)
        echo "⚙️  Configurar puertos manualmente"
        read -p "Puerto para Flask [5000]: " flask_port
        flask_port=${flask_port:-5000}
        
        read -p "Puerto para Django [5001]: " django_port
        django_port=${django_port:-5001}
        
        echo ""
        echo "📋 Configuración manual:"
        echo "   Flask: http://$IP_LOCAL:$flask_port"
        echo "   Django: http://$IP_LOCAL:$django_port"
        echo ""
        echo "⚠️  Recuerda modificar web/app.py y django_report si cambias puertos."
        ;;
    6)
        echo "👋 Saliendo..."
        exit 0
        ;;
    *)
        echo "❌ Opción inválida"
        ;;
esac