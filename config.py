# config.py - Configuración dinámica para Carne Feliz ERP
import socket
import os
import sys
from pathlib import Path

# Obtener ruta raíz del proyecto
BASE_DIR = Path(__file__).parent.absolute()

def get_local_ip():
    """Obtiene la IP local automáticamente"""
    try:
        # Método 1: Conectar a DNS externo
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 53))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            # Método 2: Nombre de host
            return socket.gethostbyname(socket.gethostname())
        except:
            # Método 3: Fallback a localhost
            return "127.0.0.1"

def detect_flask_app():
    """Detecta qué app Flask se está usando"""
    flask_dirs = ['web', 'app']
    for dir_name in flask_dirs:
        if (BASE_DIR / dir_name).exists():
            return dir_name
    return 'web'  # Default

class Config:
    """Configuración centralizada del sistema"""
    
    # Directorios
    BASE_DIR = BASE_DIR
    DATA_DIR = BASE_DIR / 'data'
    WEB_DIR = BASE_DIR / 'web'
    APP_DIR = BASE_DIR / 'app'
    DJANGO_DIR = BASE_DIR / 'django_report'
    
    # Detección automática
    LOCAL_IP = get_local_ip()
    FLASK_APP = detect_flask_app()  # 'web' o 'app'
    
    # Puertos (ajusta según tu configuración)
    FLASK_PORT = 5001 if FLASK_APP == 'web' else 5000
    DJANGO_PORT = 5000
    
    # URLs
    FLASK_URL = f"http://{LOCAL_IP}:{FLASK_PORT}"
    DJANGO_URL = f"http://{LOCAL_IP}:{DJANGO_PORT}"
    
    # Bases de datos
    DB_PRINCIPAL = DATA_DIR / 'carniceria_orm.db'
    DB_SHARED = BASE_DIR / 'shared_db'
    
    # Verificar qué DB existe
    if DB_PRINCIPAL.exists():
        DB_PATH = str(DB_PRINCIPAL)
    elif DB_SHARED.exists():
        DB_PATH = str(DB_SHARED)
    else:
        DB_PATH = str(DATA_DIR / 'carniceria.db')
    
    # Rutas de archivos
    CAJA_DIR = DATA_DIR / 'caja'
    WEB_CAJA_DIR = WEB_DIR / 'data' / 'caja'
    
    # Debug
    DEBUG = True
    
    def __str__(self):
        """Representación amigable de la configuración"""
        return f"""
        🥩 CONFIGURACIÓN CARNE FELIZ ERP 🥩
        
        📍 Directorios:
          - Raíz: {self.BASE_DIR}
          - Datos: {self.DATA_DIR}
          - Web: {self.WEB_DIR}
          - Django: {self.DJANGO_DIR}
        
        🌐 Red:
          - IP Local: {self.LOCAL_IP}
          - Flask ({self.FLASK_APP}): {self.FLASK_URL}
          - Django: {self.DJANGO_URL}
        
        🗄️ Base de datos: {self.DB_PATH}
        
        ✅ {'Django detectado' if self.DJANGO_DIR.exists() else '⚠️ Django NO encontrado'}
        ✅ {'Web Flask detectado' if self.WEB_DIR.exists() else '⚠️ Web Flask NO encontrado'}
        ✅ {'App Flask detectado' if self.APP_DIR.exists() else '⚠️ App Flask NO encontrado'}
        """

# Instancia global
config = Config()

if __name__ == "__main__":
    print(config)
    print("\n🔍 Verificando conexiones...")
    
    # Probar si podemos acceder a los servicios
    import requests
    from urllib.request import urlopen
    
    servicios = [
        ("Flask", config.FLASK_URL),
        ("Django", config.DJANGO_URL)
    ]
    
    for nombre, url in servicios:
        try:
            urlopen(url, timeout=2)
            print(f"  ✅ {nombre}: {url} (Disponible)")
        except:
            print(f"  ⚠️  {nombre}: {url} (No disponible)")