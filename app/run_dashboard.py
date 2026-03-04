# app/run_dashboard.py (ACTUALIZADO)
#!/usr/bin/env python3
"""
Script para iniciar el dashboard CLI de Carnicería
"""

import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Función principal."""
    try:
        from app.dashboard import DashboardCarniceria
        
        print("=" * 60)
        print("🥩 CARNE FELIZ - DASHBOARD CLI")
        print("=" * 60)
        print("Sistema: SQLAlchemy + Base de datos persistente")
        print("=" * 60)
        
        # Iniciar dashboard
        dashboard = DashboardCarniceria()
        dashboard.ejecutar()
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Instala las dependencias: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()