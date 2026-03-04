# app/dashboard.py (VERSIÓN ACTUALIZADA - MANTIENE TU INTERFAZ PERO USA LA NUEVA LÓGICA)
import os
import sys
import json
from datetime import datetime
from typing import Dict, List

# Para una interfaz profesional en terminal
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.columns import Columns
    from rich import box
    RICH_DISPONIBLE = True
except ImportError:
    RICH_DISPONIBLE = False
    print("Instala 'rich' para una interfaz más profesional: pip install rich")

# IMPORTAR LA NUEVA LÓGICA
from .caja import ControlCaja
from .persistencia import db_manager
from .procesos import AlertaStockManager, CreditoManager, ReporteManager
from .modelos import ProductoElaborado

class DashboardCarniceria:
    """Dashboard profesional para gestión de carnicería (CLI)."""
    
    def __init__(self):
        self.console = Console() if RICH_DISPONIBLE else None
        
        # Usamos la nueva lógica de caja (ControlCaja)
        self.caja = ControlCaja
        
        # Colores para terminal (si no hay rich)
        self.COLORES = {
            'verde': '\033[92m',
            'amarillo': '\033[93m',
            'rojo': '\033[91m',
            'azul': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'reset': '\033[0m',
            'negrita': '\033[1m'
        }
    
    def limpiar_pantalla(self):
        """Limpia la pantalla de manera cross-platform."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostrar_header_profesional(self):
        """Muestra un encabezado profesional."""
        fecha = datetime.now().strftime("%A, %d de %B de %Y")
        hora = datetime.now().strftime("%H:%M:%S")
        
        if self.console:
            header = Table(show_header=False, box=box.ROUNDED, width=80)
            header.add_column("left", justify="left")
            header.add_column("center", justify="center")
            header.add_column("right", justify="right")
            header.add_row(
                "🥩 CARNE FELIZ",
                "[bold]SISTEMA DE GESTIÓN (SQLAlchemy)[/bold]",
                f"{fecha} | {hora}"
            )
            self.console.print(header)
        else:
            print("=" * 80)
            print(f"{self.COLORES['negrita']}🥩 CARNE FELIZ - SISTEMA DE GESTIÓN (SQLAlchemy){self.COLORES['reset']}")
            print(f"{self.COLORES['azul']}{fecha} | {hora}{self.COLORES['reset']}")
            print("=" * 80)
    
    def mostrar_estado_caja(self):
        """Muestra el estado actual de la caja usando la nueva lógica."""
        try:
            estado = self.caja.obtener_estado_caja()
            
            if not estado['existe']:
                mensaje = "⚠️  CAJA NO ABIERTA - Use 'Abrir Caja' para comenzar"
                if self.console:
                    panel = Panel(
                        mensaje,
                        title="[bold]💰 ESTADO DE CAJA[/bold]",
                        border_style="yellow",
                        padding=(1, 2)
                    )
                    self.console.print(panel)
                else:
                    print(f"\n{self.COLORES['amarillo']}💰 ESTADO DE CAJA")
                    print(f"  {mensaje}{self.COLORES['reset']}")
                return
            
            if self.console:
                tabla = Table(title="💰 RESUMEN DE CAJA (SQLAlchemy)", box=box.ROUNDED)
                tabla.add_column("Concepto", style="cyan")
                tabla.add_column("Monto", justify="right", style="green")
                
                tabla.add_row("Estado", f"[bold]{estado['estado'].upper()}[/bold]")
                tabla.add_row("Fecha", estado['fecha'])
                tabla.add_row("Responsable", estado['responsable'])
                tabla.add_row("Monto Inicial", f"${estado['monto_inicial']:.2f}")
                tabla.add_row("Ventas Efectivo", f"${estado['ventas_efectivo']:.2f}")
                tabla.add_row("Ventas Tarjeta", f"${estado['ventas_tarjeta']:.2f}")
                tabla.add_row("", "")
                tabla.add_row("Total Ventas", f"[bold]${estado['total_ventas']:.2f}[/bold]")
                tabla.add_row("Total Gastos", f"${estado['gastos_dia']:.2f}")
                tabla.add_row("", "")
                tabla.add_row("Efectivo Esperado", f"[bold yellow]${estado['efectivo_esperado']:.2f}[/bold yellow]")
                
                if estado['hora_apertura']:
                    tabla.add_row("Hora Apertura", estado['hora_apertura'].split('T')[1][:8])
                if estado['hora_cierre']:
                    tabla.add_row("Hora Cierre", estado['hora_cierre'].split('T')[1][:8])
                
                self.console.print(tabla)
            else:
                print(f"\n{self.COLORES['negrita']}💰 RESUMEN DE CAJA (SQLAlchemy){self.COLORES['reset']}")
                print(f"{self.COLORES['cyan']}Estado:{self.COLORES['reset']} {estado['estado'].upper()}")
                print(f"{self.COLORES['cyan']}Fecha:{self.COLORES['reset']} {estado['fecha']}")
                print(f"{self.COLORES['cyan']}Responsable:{self.COLORES['reset']} {estado['responsable']}")
                print(f"{self.COLORES['cyan']}Monto Inicial:{self.COLORES['reset']} ${estado['monto_inicial']:.2f}")
                print(f"{self.COLORES['cyan']}Ventas Efectivo:{self.COLORES['reset']} ${estado['ventas_efectivo']:.2f}")
                print(f"{self.COLORES['cyan']}Ventas Tarjeta:{self.COLORES['reset']} ${estado['ventas_tarjeta']:.2f}")
                print(f"{self.COLORES['cyan']}Total Ventas:{self.COLORES['reset']} {self.COLORES['negrita']}${estado['total_ventas']:.2f}{self.COLORES['reset']}")
                print(f"{self.COLORES['cyan']}Total Gastos:{self.COLORES['reset']} ${estado['gastos_dia']:.2f}")
                print(f"{self.COLORES['amarillo']}Efectivo Esperado:{self.COLORES['reset']} {self.COLORES['negrita']}${estado['efectivo_esperado']:.2f}{self.COLORES['reset']}")
                if estado['hora_apertura']:
                    print(f"{self.COLORES['cyan']}Hora Apertura:{self.COLORES['reset']} {estado['hora_apertura'].split('T')[1][:8]}")
                if estado['hora_cierre']:
                    print(f"{self.COLORES['cyan']}Hora Cierre:{self.COLORES['reset']} {estado['hora_cierre'].split('T')[1][:8]}")
                
        except Exception as e:
            error_msg = f"Error al obtener estado de caja: {str(e)}"
            if self.console:
                self.console.print(f"[red]{error_msg}[/red]")
            else:
                print(f"{self.COLORES['rojo']}{error_msg}{self.COLORES['reset']}")
    
    def mostrar_inventario_critico(self):
        """Muestra productos con stock crítico usando la nueva lógica."""
        try:
            alerta_manager = AlertaStockManager()
            alertas = alerta_manager.generar_alertas()
            
            if not alertas:
                mensaje = "✅ Todos los productos con stock adecuado"
                if self.console:
                    panel = Panel(mensaje, title="📦 INVENTARIO", border_style="green")
                    self.console.print(panel)
                else:
                    print(f"\n{self.COLORES['verde']}📦 INVENTARIO")
                    print(f"  {mensaje}{self.COLORES['reset']}")
                return
            
            if self.console:
                tabla = Table(title="⚠️  PRODUCTOS CON STOCK BAJO", box=box.SIMPLE)
                tabla.add_column("Producto", style="red")
                tabla.add_column("Tipo", style="cyan")
                tabla.add_column("Stock Actual", justify="right")
                tabla.add_column("Umbral", justify="right")
                tabla.add_column("Faltan", justify="right")
                
                for alerta in alertas[:5]:
                    tabla.add_row(
                        alerta['producto'],
                        alerta['tipo'],
                        f"{alerta['stock_actual']:.1f} kg",
                        f"{alerta['umbral']:.1f} kg",
                        f"{alerta['diferencia']:.1f} kg"
                    )
                
                self.console.print(tabla)
            else:
                print(f"\n{self.COLORES['rojo']}⚠️  PRODUCTOS CON STOCK BAJO{self.COLORES['reset']}")
                for alerta in alertas[:5]:
                    print(f"  {alerta['producto']} ({alerta['tipo']}): {alerta['stock_actual']:.1f} kg < {alerta['umbral']:.1f} kg (faltan {alerta['diferencia']:.1f} kg)")
        except Exception as e:
            error_msg = f"Error al obtener inventario: {str(e)}"
            if self.console:
                self.console.print(f"[red]{error_msg}[/red]")
            else:
                print(f"{self.COLORES['rojo']}{error_msg}{self.COLORES['reset']}")
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal interactivo."""
        if self.console:
            opciones = [
                ("[1]", "💰 Abrir Caja"),
                ("[2]", "🛒 Nueva Venta"),
                ("[3]", "📊 Ver Estado Completo"),
                ("[4]", "💸 Registrar Gasto"),
                ("[5]", "📋 Ver Movimientos"),
                ("[6]", "🔒 Cerrar Caja"),
                ("[7]", "📦 Ver Inventario"),
                ("[8]", "📈 Reporte Diario"),
                ("[9]", "🌐 Ir a Web Dashboard"),
                ("[0]", "🚪 Salir")
            ]
            
            col1 = "\n".join([f"{num} {texto}" for num, texto in opciones[:5]])
            col2 = "\n".join([f"{num} {texto}" for num, texto in opciones[5:]])
            
            panel = Panel(
                Columns([col1, col2], equal=True, expand=True),
                title="📋 MENÚ PRINCIPAL (CLI)",
                border_style="cyan",
                padding=(1, 3)
            )
            self.console.print(panel)
        else:
            print(f"\n{self.COLORES['negrita']}📋 MENÚ PRINCIPAL (CLI){self.COLORES['reset']}")
            print(f"{self.COLORES['cyan']}[1] 💰 Abrir Caja{self.COLORES['reset']}")
            print(f"{self.COLORES['cyan']}[2] 🛒 Nueva Venta{self.COLORES['reset']}")
            print(f"{self.COLORES['cyan']}[3] 📊 Ver Estado Completo{self.COLORES['reset']}")
            print(f"{self.COLORES['cyan']}[4] 💸 Registrar Gasto{self.COLORES['reset']}")
            print(f"{self.COLORES['cyan']}[5] 📋 Ver Movimientos{self.COLORES['reset']}")
            print(f"{self.COLORES['cyan']}[6] 🔒 Cerrar Caja{self.COLORES['reset']}")
            print(f"{self.COLORES['cyan']}[7] 📦 Ver Inventario{self.COLORES['reset']}")
            print(f"{self.COLORES['cyan']}[8] 📈 Reporte Diario{self.COLORES['reset']}")
            print(f"{self.COLORES['azul']}[9] 🌐 Ir a Web Dashboard{self.COLORES['reset']}")
            print(f"{self.COLORES['rojo']}[0] 🚪 Salir{self.COLORES['reset']}")
    
    def abrir_caja_interactivo(self):
        """Interfaz interactiva para abrir caja usando la nueva lógica."""
        self.limpiar_pantalla()
        self.mostrar_header_profesional()
        
        print(f"\n{self.COLORES['negrita']}💰 APERTURA DE CAJA{self.COLORES['reset']}")
        print(self.COLORES['amarillo'] + "="*40 + self.COLORES['reset'])

        try:
            monto = float(input("Monto inicial en caja: $"))
            responsable = input("Responsable: ").strip()
            
            if not responsable:
                responsable = "Administrador"
            
            # Usar la nueva lógica
            caja = self.caja.abrir_caja(monto, responsable)
            
            print(f"\n{self.COLORES['verde']}✅ Caja abierta correctamente{self.COLORES['reset']}")
            print(f"  Fondo inicial: ${monto:.2f}")
            print(f"  Responsable: {responsable}")
            print(f"  ID Caja: {caja.id}")
            
        except ValueError as e:
            print(f"\n{self.COLORES['rojo']}❌ Error: {str(e)}{self.COLORES['reset']}")
        except Exception as e:
            print(f"\n{self.COLORES['rojo']}❌ Error inesperado: {str(e)}{self.COLORES['reset']}")
        
        input("\nPresione Enter para continuar...")
    
    def cerrar_caja_interactivo(self):
        """Interfaz interactiva para cerrar caja usando la nueva lógica."""
        self.limpiar_pantalla()
        self.mostrar_header_profesional()
        
        estado = self.caja.obtener_estado_caja()
        if not estado['existe'] or estado['estado'] != 'abierta':
            print(f"\n{self.COLORES['rojo']}❌ Error: La caja no está abierta{self.COLORES['reset']}")
            input("\nPresione Enter para continuar...")
            return
        
        print(f"\n{self.COLORES['negrita']}🔒 CIERRE DE CAJA{self.COLORES['reset']}")
        print(self.COLORES['amarillo'] + "="*40 + self.COLORES['reset'])

        
        print(f"\n{self.COLORES['cyan']}Resumen actual:{self.COLORES['reset']}")
        print(f"  Efectivo esperado: ${estado['efectivo_esperado']:.2f}")
        print(f"  Total ventas: ${estado['total_ventas']:.2f}")
        print(f"  Total gastos: ${estado['gastos_dia']:.2f}")
        
        try:
            efectivo_real = float(input("\nEfectivo real contado: $"))
            
            # Usar la nueva lógica
            caja = self.caja.cerrar_caja(efectivo_real)
            
            print(f"\n{self.COLORES['verde']}✅ Caja cerrada correctamente{self.COLORES['reset']}")
            print(f"  Efectivo real: ${efectivo_real:.2f}")
            print(f"  Efectivo esperado: ${caja.efectivo_esperado:.2f}")
            
            diferencia = caja.diferencia
            if diferencia == 0:
                print(f"  {self.COLORES['verde']}✨ Diferencia: $0.00 (Perfecto!){self.COLORES['reset']}")
            elif diferencia > 0:
                print(f"  {self.COLORES['amarillo']}📈 Sobra: ${diferencia:.2f}{self.COLORES['reset']}")
            else:
                print(f"  {self.COLORES['rojo']}📉 Falta: ${abs(diferencia):.2f}{self.COLORES['reset']}")
            
            # Generar reporte (opcional)
            print(f"\n{self.COLORES['azul']}📄 Reporte guardado en base de datos{self.COLORES['reset']}")
            
        except ValueError as e:
            print(f"\n{self.COLORES['rojo']}❌ Error: {str(e)}{self.COLORES['reset']}")
        except Exception as e:
            print(f"\n{self.COLORES['rojo']}❌ Error inesperado: {str(e)}{self.COLORES['reset']}")
        
        input("\nPresione Enter para continuar...")
    
    def ver_movimientos(self):
        """Muestra movimientos del día."""
        self.limpiar_pantalla()
        self.mostrar_header_profesional()
        
        try:
            movimientos = self.caja.obtener_movimientos_dia()
            
            if not movimientos:
                print(f"\n{self.COLORES['amarillo']}📋 No hay movimientos registrados hoy{self.COLORES['reset']}")
                input("\nPresione Enter para continuar...")
                return
            
            if self.console:
                tabla = Table(title="📋 MOVIMIENTOS DEL DÍA", box=box.SIMPLE)
                tabla.add_column("Hora", style="cyan")
                tabla.add_column("Tipo", style="yellow")
                tabla.add_column("Monto", justify="right", style="green")
                tabla.add_column("Detalles")
                
                for mov in movimientos[:15]:
                    color = "green" if mov['monto'] > 0 else "red"
                    tipo_icon = "🛒" if mov['tipo'] == 'VENTA' else "💸"
                    tipo_text = f"{tipo_icon} {mov['tipo']}"
                    if mov['tipo_pago']:
                        tipo_text += f" ({mov['tipo_pago']})"
                    
                    tabla.add_row(
                        mov['hora'],
                        tipo_text,
                        f"[{color}]${mov['monto']:.2f}[/{color}]",
                        mov['detalles'][:30] + "..." if len(mov['detalles']) > 30 else mov['detalles']
                    )
                
                self.console.print(tabla)
            else:
                print(f"\n{self.COLORES['negrita']}📋 MOVIMIENTOS DEL DÍA{self.COLORES['reset']}")
                for mov in movimientos[:15]:
                    color = self.COLORES['verde'] if mov['monto'] > 0 else self.COLORES['rojo']
                    tipo_icon = "🛒" if mov['tipo'] == 'VENTA' else "💸"
                    print(f"  {mov['hora']} | {tipo_icon} {mov['tipo']}", end="")
                    if mov['tipo_pago']:
                        print(f" ({mov['tipo_pago']})", end="")
                    print(f" | {color}${mov['monto']:.2f}{self.COLORES['reset']} | {mov['detalles'][:30]}")
            
            print(f"\n{self.COLORES['cyan']}Total movimientos: {len(movimientos)}{self.COLORES['reset']}")
            
        except Exception as e:
            print(f"\n{self.COLORES['rojo']}❌ Error: {str(e)}{self.COLORES['reset']}")
        
        input("\nPresione Enter para continuar...")
    
    def ejecutar(self):
        """Ejecuta el dashboard principal."""
        while True:
            self.limpiar_pantalla()
            self.mostrar_header_profesional()
            
            # Mostrar métricas clave
            self.mostrar_estado_caja()
            print()  # Espacio
            self.mostrar_inventario_critico()
            
            # Mostrar menú
            self.mostrar_menu_principal()
            
            # Leer opción
            opcion = input(f"\n{self.COLORES['cyan']}Seleccione una opción: {self.COLORES['reset']}")
            
            if opcion == "1":
                self.abrir_caja_interactivo()
            elif opcion == "2":
                self.nueva_venta_interactivo()
            elif opcion == "3":
                self.ver_estado_completo()
            elif opcion == "4":
                self.registrar_gasto_interactivo()
            elif opcion == "5":
                self.ver_movimientos()
            elif opcion == "6":
                self.cerrar_caja_interactivo()
            elif opcion == "7":
                self.ver_inventario_completo()
            elif opcion == "8":
                self.generar_reporte_diario()
            elif opcion == "9":
                self.iniciar_web_dashboard()
            elif opcion == "0":
                print(f"\n{self.COLORES['verde']}👋 ¡Hasta luego!{self.COLORES['reset']}")
                break
            else:
                print(f"\n{self.COLORES['rojo']}❌ Opción inválida{self.COLORES['reset']}")
                input("Presione Enter para continuar...")
    
    def iniciar_web_dashboard(self):
        """Inicia el dashboard web."""
        print(f"\n{self.COLORES['azul']}🌐 Iniciando dashboard web...{self.COLORES['reset']}")
        print(f"  Abre tu navegador en: {self.COLORES['negrita']}http://localhost:5000{self.COLORES['reset']}")
        print(f"  Presiona Ctrl+C en esta terminal para detener el servidor web")
        
        try:
            # Ejecutar el servidor web en segundo plano
            import subprocess
            import sys
            
            # Ruta al script de inicio web
            web_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web', 'app.py')
            
            if os.path.exists(web_script):
                print(f"\n{self.COLORES['verde']}✅ Servidor web iniciado{self.COLORES['reset']}")
                print(f"{self.COLORES['amarillo']}⚠️  Nota: El servidor web se ejecutará en una nueva terminal{self.COLORES['reset']}")
                
                # Dependiendo del sistema operativo
                if os.name == 'nt':  # Windows
                    subprocess.Popen(['start', 'cmd', '/k', f'python "{web_script}"'], shell=True)
                else:  # Linux/Mac
                    subprocess.Popen(['xterm', '-e', f'python3 "{web_script}"'])
                
                input(f"\n{self.COLORES['cyan']}Presiona Enter para volver al menú CLI...{self.COLORES['reset']}")
            else:
                print(f"\n{self.COLORES['rojo']}❌ No se encontró el servidor web{self.COLORES['reset']}")
                print(f"  Ruta esperada: {web_script}")
                input("\nPresione Enter para continuar...")
                
        except Exception as e:
            print(f"\n{self.COLORES['rojo']}❌ Error al iniciar web: {str(e)}{self.COLORES['reset']}")
            input("\nPresione Enter para continuar...")
    
    # Métodos placeholder para otras funcionalidades (mantener tus originales)
    def nueva_venta_interactivo(self):
        print(f"\n{self.COLORES['amarillo']}🛒 Nueva Venta - Usa la interfaz web en http://localhost:5000/ventas{self.COLORES['reset']}")
        input("Presione Enter para continuar...")
    
    def ver_estado_completo(self):
        print(f"\n{self.COLORES['amarillo']}📊 Estado Completo - Usa la interfaz web en http://localhost:5000{self.COLORES['reset']}")
        input("Presione Enter para continuar...")
    
    def registrar_gasto_interactivo(self):
        print(f"\n{self.COLORES['amarillo']}💸 Registrar Gasto - Usa la interfaz web en http://localhost:5000/caja{self.COLORES['reset']}")
        input("Presione Enter para continuar...")
    
    def ver_inventario_completo(self):
        print(f"\n{self.COLORES['amarillo']}📦 Ver Inventario Completo - Usa la interfaz web en http://localhost:5000/ventas{self.COLORES['reset']}")
        input("Presione Enter para continuar...")
    
def generar_reporte_diario(self):
    print(
        f"\n{self.COLORES['amarillo']}"
        "📈 Reporte Diario - Usa la interfaz web en http://localhost:5000/reportes"
        f"{self.COLORES['reset']}"
    )
    input("Presione Enter para continuar...")

    input("Presione Enter para continuar...")