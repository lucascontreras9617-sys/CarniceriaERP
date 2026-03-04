#!/usr/bin/env python3
"""
CARNE FELIZ - Sistema Web Completo
Versión: 2.4.0 (Con configuración dinámica)
"""
import os
import sys
import warnings
import socket
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
import requests

# ==================== SUPRIMIR WARNINGS ====================
warnings.filterwarnings("ignore")

# ==================== CONFIGURACIÓN DE PATH ====================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(PROJECT_ROOT, 'app')

# Limpiar paths duplicados
if APP_DIR in sys.path:
    sys.path.remove(APP_DIR)
if PROJECT_ROOT in sys.path:
    sys.path.remove(PROJECT_ROOT)
    
sys.path.insert(0, APP_DIR)
sys.path.insert(0, PROJECT_ROOT)

print(f"🔧 Configurando paths...")
print(f"   PROJECT_ROOT: {PROJECT_ROOT}")
print(f"   APP_DIR: {APP_DIR}")

# ==================== CONFIGURACIÓN DINÁMICA ====================
def get_local_ip():
    """Obtiene la IP local automáticamente"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 53))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "127.0.0.1"

# Configuración centralizada
class ConfigDinamica:
    """Configuración dinámica del sistema"""
    
    def __init__(self):
        # IP y puertos
        self.LOCAL_IP = get_local_ip()
        self.FLASK_PORT = 5000  # Puerto de esta aplicación Flask
        self.DJANGO_PORT = 5000  # Puerto donde corre Django
        
        # URLs completas
        self.FLASK_URL = f"http://{self.LOCAL_IP}:{self.FLASK_PORT}"
        self.DJANGO_URL = f"http://{self.LOCAL_IP}:{self.DJANGO_PORT}"
        
        # Directorios importantes
        self.DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
        self.WEB_DIR = os.path.join(PROJECT_ROOT, 'web')
        self.DJANGO_DIR = os.path.join(PROJECT_ROOT, 'django_report')
        
        # Base de datos
        self.DB_PATH = os.path.join(self.DATA_DIR, 'carniceria_orm.db')
        
        # Estado
        self.DJANGO_DISPONIBLE = self._verificar_django()
    
    def _verificar_django(self):
        """Verifica si Django está disponible"""
        try:
            response = requests.get(f"{self.DJANGO_URL}/", timeout=2)
            return response.status_code < 400
        except:
            return False
    
    def __str__(self):
        return f"""
        🥩 CONFIGURACIÓN DETECTADA:
          IP Local: {self.LOCAL_IP}
          Flask URL: {self.FLASK_URL}
          Django URL: {self.DJANGO_URL}
          Django disponible: {'✅' if self.DJANGO_DISPONIBLE else '❌'}
        """

# Crear instancia de configuración
config = ConfigDinamica()
print(config)

# ==================== CONFIGURAR FLASK ====================
app = Flask(__name__)
app.secret_key = 'carniceria_secret_key_2024'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configurar CORS
CORS(app)

# Context processor para pasar configuración a todas las plantillas
@app.context_processor
def inject_global_config():
    """Inyecta configuración global en todas las plantillas"""
    return {
        'config': config,
        'django_url': config.DJANGO_URL,
        'flask_url': config.FLASK_URL,
        'current_year': datetime.now().year,
        'app_name': '🥩 Carne Feliz ERP'
    }

# ==================== SIMULADOR BACKEND ====================
class SimuladorBackend:
    """Simulador completo para desarrollo."""
    
    def __init__(self):
        self.caja_estado = {
            "estado": "cerrada",
            "responsable": "",
            "monto_inicial": 0,
            "ventas_efectivo": 0,
            "ventas_tarjeta": 0,
            "gastos_dia": 0
        }
        self.movimientos = []
        self.productos = [
            {"id": "1", "nombre": "Vacio", "precio": 12.99, "stock": 50.0, "unidad": "kg", "categoria": "CORTES"},
            {"id": "2", "nombre": "Bife de Chorizo", "precio": 15.50, "stock": 30.0, "unidad": "kg", "categoria": "CORTES"},
            {"id": "3", "nombre": "Nalga", "precio": 7.00, "stock": 40.0, "unidad": "kg", "categoria": "CORTES"},
            {"id": "4", "nombre": "Asado", "precio": 10.99, "stock": 25.0, "unidad": "kg", "categoria": "CORTES"},
            {"id": "5", "nombre": "Costillas", "precio": 9.25, "stock": 35.0, "unidad": "kg", "categoria": "CORTES"},
            {"id": "6", "nombre": "Carne Molida", "precio": 8.50, "stock": 60.0, "unidad": "kg", "categoria": "MOLIDA"},
            {"id": "7", "nombre": "Chorizo", "precio": 9.75, "stock": 45.0, "unidad": "kg", "categoria": "EMBUTIDOS"},
            {"id": "8", "nombre": "Morcilla", "precio": 7.25, "stock": 30.0, "unidad": "kg", "categoria": "EMBUTIDOS"},
        ]
        self.ventas_contador = 0
    
    def obtener_estado_caja(self):
        estado = self.caja_estado.copy()
        estado['existe'] = estado['estado'] == 'abierta'
        estado['hora_actual'] = datetime.now().strftime("%H:%M:%S")
        estado['fecha_actual'] = datetime.now().strftime("%Y-%m-%d")
        estado['total_ventas'] = estado['ventas_efectivo'] + estado['ventas_tarjeta']
        estado['efectivo_esperado'] = estado['monto_inicial'] + estado['ventas_efectivo'] - estado['gastos_dia']
        estado['cantidad_ventas'] = len([m for m in self.movimientos if m.get('tipo') == 'VENTA'])
        estado['hora_apertura'] = "09:00:00"
        
        if estado['estado'] == 'abierta':
            estado['mensaje'] = f"Caja abierta por {estado['responsable']}"
        else:
            estado['mensaje'] = "Caja cerrada"
        
        return estado
    
    def abrir_caja(self, monto, responsable):
        try:
            monto_float = float(monto)
            if monto_float <= 0:
                return {"success": False, "error": "Monto debe ser mayor a 0"}
            
            self.caja_estado = {
                "estado": "abierta",
                "responsable": responsable,
                "monto_inicial": monto_float,
                "ventas_efectivo": 0,
                "ventas_tarjeta": 0,
                "gastos_dia": 0
            }
            
            self.movimientos.append({
                'tipo': 'APERTURA',
                'monto': monto_float,
                'hora': datetime.now().strftime('%H:%M:%S'),
                'detalles': f"Apertura por {responsable}",
                'concepto': 'Apertura'
            })
            
            return {
                "success": True,
                "monto": monto_float,
                "responsable": responsable,
                "mensaje": "Caja abierta exitosamente"
            }
        except ValueError:
            return {"success": False, "error": "Monto inválido"}
    
    def cerrar_caja(self, efectivo_real):
        try:
            efectivo = float(efectivo_real)
            estado = self.obtener_estado_caja()
            diferencia = efectivo - estado['efectivo_esperado']
            
            self.caja_estado['estado'] = 'cerrada'
            
            self.movimientos.append({
                'tipo': 'CIERRE',
                'monto': efectivo,
                'hora': datetime.now().strftime('%H:%M:%S'),
                'detalles': f"Cierre. Efectivo: ${efectivo:.2f}",
                'concepto': 'Cierre'
            })
            
            return {
                "success": True,
                "cierre": {
                    "efectivo_esperado": estado['efectivo_esperado'],
                    "efectivo_real": efectivo,
                    "diferencia": diferencia
                },
                "mensaje": "Caja cerrada exitosamente"
            }
        except ValueError:
            return {"success": False, "error": "Efectivo inválido"}
    
    def registrar_venta(self, tipo_pago, monto, detalles="", cliente_nombre=""):
        try:
            monto_float = float(monto)
            if monto_float <= 0:
                return {"success": False, "error": "Monto debe ser mayor a 0"}
            
            tipo_pago = tipo_pago.upper()
            if tipo_pago not in ['EFECTIVO', 'TARJETA', 'TRANSFERENCIA']:
                return {"success": False, "error": "Tipo de pago inválido"}
            
            if self.caja_estado['estado'] != 'abierta':
                return {"success": False, "error": "Caja cerrada"}
            
            if tipo_pago == 'EFECTIVO':
                self.caja_estado['ventas_efectivo'] += monto_float
            elif tipo_pago == 'TARJETA':
                self.caja_estado['ventas_tarjeta'] += monto_float
            
            self.ventas_contador += 1
            venta_id = f"SIM-{self.ventas_contador:04d}"
            
            self.movimientos.append({
                'tipo': 'VENTA',
                'tipo_pago': tipo_pago,
                'monto': monto_float,
                'hora': datetime.now().strftime('%H:%M:%S'),
                'detalles': detalles or f"Venta #{venta_id}",
                'concepto': 'Venta',
                'cliente': cliente_nombre or "Cliente"
            })
            
            return {
                "success": True,
                "venta_id": venta_id,
                "monto": monto_float,
                "tipo_pago": tipo_pago,
                "hora": datetime.now().strftime('%H:%M:%S'),
                "mensaje": f"Venta registrada: ${monto_float:.2f}"
            }
        except ValueError:
            return {"success": False, "error": "Monto inválido"}
    
    def obtener_movimientos(self, limite=50):
        movimientos_ordenados = sorted(
            self.movimientos,
            key=lambda x: x.get('hora', ''),
            reverse=True
        )[:limite]
        
        return {
            "movimientos": movimientos_ordenados,
            "total": len(self.movimientos),
            "resumen": {
                "total_ventas": self.caja_estado['ventas_efectivo'] + self.caja_estado['ventas_tarjeta'],
                "total_gastos": self.caja_estado['gastos_dia'],
                "balance": (self.caja_estado['ventas_efectivo'] + self.caja_estado['ventas_tarjeta']) - self.caja_estado['gastos_dia']
            }
        }
    
    def obtener_productos(self, filtro="", solo_bajo_stock=False):
        productos_filtrados = self.productos
        
        if filtro:
            filtro_lower = filtro.lower()
            productos_filtrados = [
                p for p in productos_filtrados 
                if filtro_lower in p['nombre'].lower() or filtro_lower in p['categoria'].lower()
            ]
        
        if solo_bajo_stock:
            productos_filtrados = [p for p in productos_filtrados if p['stock'] < 10]
        
        for p in productos_filtrados:
            if p['stock'] <= 0:
                p['nivel_stock'] = 'AGOTADO'
                p['stock_class'] = 'no-stock'
            elif p['stock'] < 5:
                p['nivel_stock'] = 'BAJO'
                p['stock_class'] = 'low-stock'
            else:
                p['nivel_stock'] = 'NORMAL'
                p['stock_class'] = 'normal-stock'
        
        return productos_filtrados
    
    def registrar_gasto(self, descripcion, monto, categoria="GASTO"):
        try:
            monto_float = float(monto)
            if monto_float <= 0:
                return {"success": False, "error": "Monto debe ser mayor a 0"}
            
            if self.caja_estado['estado'] != 'abierta':
                return {"success": False, "error": "Caja cerrada"}
            
            self.caja_estado['gastos_dia'] += monto_float
            
            self.movimientos.append({
                'tipo': 'GASTO',
                'monto': -monto_float,
                'hora': datetime.now().strftime('%H:%M:%S'),
                'detalles': descripcion,
                'categoria': categoria,
                'concepto': 'Gasto'
            })
            
            return {
                "success": True,
                "monto": monto_float,
                "descripcion": descripcion,
                "categoria": categoria,
                "mensaje": f"Gasto registrado: ${monto_float:.2f}"
            }
        except ValueError:
            return {"success": False, "error": "Monto inválido"}
    
    def generar_reporte_ventas(self, fecha_inicio=None, fecha_fin=None):
        if not fecha_inicio:
            fecha_inicio = datetime.now().strftime('%Y-%m-%d')
        if not fecha_fin:
            fecha_fin = datetime.now().strftime('%Y-%m-%d')
        
        try:
            inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            dias = (fin - inicio).days + 1
        except:
            dias = 1
        
        total_ventas = 125000.50 * dias
        cantidad_ventas = 342 * dias
        
        return {
            "periodo": {
                "inicio": fecha_inicio,
                "fin": fecha_fin,
                "dias": dias
            },
            "resumen": {
                "total_ventas": total_ventas,
                "cantidad_ventas": cantidad_ventas,
                "promedio_diario": total_ventas / dias if dias > 0 else total_ventas,
                "promedio_ticket": total_ventas / cantidad_ventas if cantidad_ventas > 0 else 0
            },
            "por_tipo_pago": {
                "EFECTIVO": total_ventas * 0.7,
                "TARJETA": total_ventas * 0.3
            },
            "productos_mas_vendidos": [
                {"producto": "Carne Molida", "cantidad": 120.5 * dias, "total": 1807.50 * dias},
                {"producto": "Vacio", "cantidad": 85.3 * dias, "total": 1108.90 * dias},
                {"producto": "Asado", "cantidad": 67.8 * dias, "total": 745.80 * dias},
                {"producto": "Bife de Chorizo", "cantidad": 45.2 * dias, "total": 700.60 * dias},
                {"producto": "Costillas", "cantidad": 55.7 * dias, "total": 515.23 * dias}
            ],
            "ventas_por_dia": [
                {"fecha": fecha_inicio, "total": 4200.00, "cantidad": 12}
            ],
            "modo": "simulacion"
        }
    
    def generar_reporte_inventario(self):
        return {
            "total_productos": 45,
            "valor_total_inventario": 85000.75,
            "productos_bajo_stock": 3,
            "productos_agotados": 0,
            "productos_por_categoria": {
                "CORTES": 25,
                "EMBUTIDOS": 12,
                "AVES": 8
            },
            "productos_criticos": [
                {"nombre": "Pechuga de Pollo", "stock": 0.5, "umbral": 5.0},
                {"nombre": "Chorizo", "stock": 2.0, "umbral": 10.0},
                {"nombre": "Morcilla", "stock": 3.0, "umbral": 10.0},
                {"nombre": "Vacio", "stock": 1.5, "umbral": 5.0},
                {"nombre": "Costillas", "stock": 4.0, "umbral": 10.0}
            ],
            "modo": "simulacion"
        }

# Crear instancia del simulador
simulador = SimuladorBackend()
print("✅ Simulador backend creado")

# ==================== RUTAS PRINCIPALES ====================
@app.route('/')
def index():
    try:
        estado_caja = simulador.obtener_estado_caja()
        
        return render_template('dashboard.html',
            fecha=datetime.now().strftime('%d/%m/%Y'),
            hora=datetime.now().strftime('%H:%M'),
            estado_caja=estado_caja,
            modo_simulacion=True
        )
    except Exception as e:
        print(f"❌ Error en index: {e}")
        # SOLUCIÓN TEMPORAL: En lugar de error.html, devolver página de error simple
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error - Carne Feliz</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 50px;
                    text-align: center;
                    background: #f8f9fa;
                }}
                .error {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    max-width: 600px;
                    margin: 0 auto;
                }}
                h1 {{ color: #dc3545; }}
                .btn {{
                    display: inline-block;
                    padding: 10px 20px;
                    background: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="error">
                <h1>⚠️ Error cargando dashboard</h1>
                <p><strong>Detalles:</strong> {str(e)}</p>
                <p>Posible problema: Error de sintaxis en plantilla dashboard.html (línea 636)</p>
                <a href="/caja" class="btn">Ir a Caja</a>
                <a href="/ventas" class="btn">Ir a Ventas</a>
                <a href="/reportes" class="btn">Ir a Reportes</a>
            </div>
        </body>
        </html>
        """, 500

@app.route('/caja')
def caja():
    return render_template('caja.html', modo_simulacion=True)

@app.route('/ventas')
def ventas():
    return render_template('ventas.html', modo_simulacion=True)

# ==================== RUTAS DE REPORTES EN FLASK ====================
@app.route('/reportes')
def reportes_flask():
    """Página principal de reportes implementada en Flask"""
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    fecha_hace_7_dias = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Obtener datos de ejemplo para mostrar en la página
    reporte_ventas = simulador.generar_reporte_ventas(fecha_hace_7_dias, fecha_actual)
    reporte_inventario = simulador.generar_reporte_inventario()
    
    return render_template('reportes_flask.html',
                         fecha_actual=fecha_actual,
                         fecha_hace_7_dias=fecha_hace_7_dias,
                         reporte_ventas=reporte_ventas,
                         reporte_inventario=reporte_inventario)

@app.route('/api/reportes/ventas-filtradas', methods=['GET'])
def api_ventas_filtradas():
    """API para obtener ventas filtradas por fecha"""
    try:
        fecha_inicio = request.args.get('fecha_inicio', '')
        fecha_fin = request.args.get('fecha_fin', '')
        
        # Si no vienen fechas, usar valores por defecto
        if not fecha_inicio:
            fecha_inicio = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        if not fecha_fin:
            fecha_fin = datetime.now().strftime('%Y-%m-%d')
        
        # Usar tu simulador existente que ya funciona
        reporte = simulador.generar_reporte_ventas(fecha_inicio, fecha_fin)
        
        # Asegurar que tenga los campos que el JavaScript necesita
        if 'productos_mas_vendidos' in reporte:
            reporte['productos_top'] = reporte['productos_mas_vendidos']
        
        # Agregar el campo 'success' que el JavaScript busca
        reporte['success'] = True
        
        return jsonify(reporte)
        
    except Exception as e:
        print(f"❌ Error en api_ventas_filtradas: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'detalles': str(e)
        }), 500

@app.route('/api/reportes/exportar-pdf', methods=['POST'])
def api_exportar_pdf():
    """API para exportar reporte a PDF (simulado)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No hay datos'})
    
    # Simular generación de PDF
    import uuid
    pdf_id = str(uuid.uuid4())[:8]
    
    return jsonify({
        'success': True,
        'mensaje': 'Reporte exportado exitosamente',
        'archivo': f'reporte_ventas_{pdf_id}.pdf',
        'url_descarga': f'/static/reportes/reporte_{pdf_id}.pdf',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/reportes/exportar-excel', methods=['POST'])
def api_exportar_excel():
    """API para exportar reporte a Excel (simulado)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No hay datos'})
    
    # Simular generación de Excel
    import uuid
    excel_id = str(uuid.uuid4())[:8]
    
    return jsonify({
        'success': True,
        'mensaje': 'Reporte exportado exitosamente',
        'archivo': f'reporte_ventas_{excel_id}.xlsx',
        'url_descarga': f'/static/reportes/reporte_{excel_id}.xlsx',
        'timestamp': datetime.now().isoformat()
    })

# ==================== API ENDPOINTS ====================
@app.route('/api/estado-caja', methods=['GET'])
def api_estado_caja():
    try:
        estado = simulador.obtener_estado_caja()
        return jsonify(estado)
    except Exception as e:
        print(f"❌ Error en api_estado_caja: {e}")
        return jsonify({
            "estado": "error",
            "mensaje": "Error obteniendo estado",
            "existe": False,
            "hora_actual": datetime.now().strftime("%H:%M:%S")
        }), 500

@app.route('/api/abrir-caja', methods=['POST'])
def api_abrir_caja():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos no proporcionados"}), 400
        
        monto = data.get('monto')
        responsable = data.get('responsable', 'Administrador')
        
        if not monto:
            return jsonify({"success": False, "error": "Monto requerido"}), 400
        
        resultado = simulador.abrir_caja(monto, responsable)
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error en api_abrir_caja: {e}")
        return jsonify({"success": False, "error": "Error del sistema"}), 500

@app.route('/api/registrar-venta', methods=['POST'])
def api_registrar_venta():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos no proporcionados"}), 400
        
        monto = data.get('monto')
        tipo_pago = data.get('tipo_pago', 'EFECTIVO')
        
        if not monto:
            return jsonify({"success": False, "error": "Monto requerido"}), 400
        
        resultado = simulador.registrar_venta(tipo_pago, monto)
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error en api_registrar_venta: {e}")
        return jsonify({"success": False, "error": "Error del sistema"}), 500

@app.route('/api/registrar-gasto', methods=['POST'])
def api_registrar_gasto():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos no proporcionados"}), 400
        
        descripcion = data.get('descripcion')
        monto = data.get('monto')
        
        if not descripcion or not monto:
            return jsonify({"success": False, "error": "Descripción y monto requeridos"}), 400
        
        resultado = simulador.registrar_gasto(descripcion, monto)
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error en api_registrar_gasto: {e}")
        return jsonify({"success": False, "error": "Error del sistema"}), 500

@app.route('/api/movimientos', methods=['GET'])
def api_movimientos():
    try:
        limite = request.args.get('limite', 50, type=int)
        resultado = simulador.obtener_movimientos(limite)
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error en api_movimientos: {e}")
        return jsonify({
            "movimientos": [],
            "total": 0,
            "resumen": {"total_ventas": 0, "total_gastos": 0, "balance": 0}
        }), 500

@app.route('/api/cerrar-caja', methods=['POST'])
def api_cerrar_caja():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos no proporcionados"}), 400
        
        efectivo_real = data.get('efectivo_real')
        if not efectivo_real:
            return jsonify({"success": False, "error": "Efectivo real requerido"}), 400
        
        resultado = simulador.cerrar_caja(efectivo_real)
        return jsonify(resultado)
    except Exception as e:
        print(f"❌ Error en api_cerrar_caja: {e}")
        return jsonify({"success": False, "error": "Error del sistema"}), 500

@app.route('/api/productos', methods=['GET'])
def api_productos():
    try:
        filtro = request.args.get('filtro', '')
        solo_bajo_stock = request.args.get('solo_bajo_stock', 'false').lower() == 'true'
        
        productos = simulador.obtener_productos(filtro, solo_bajo_stock)
        return jsonify({"productos": productos})
    except Exception as e:
        print(f"❌ Error en api_productos: {e}")
        return jsonify({"productos": []}), 500

@app.route('/api/reporte-ventas', methods=['GET'])
def api_reporte_ventas():
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        reporte = simulador.generar_reporte_ventas(fecha_inicio, fecha_fin)
        
        reporte['generado_en'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        reporte['modo_simulacion'] = True
        
        return jsonify(reporte)
    except Exception as e:
        print(f"❌ Error en api_reporte_ventas: {e}")
        return jsonify({"error": "Error generando reporte de ventas", "detalles": str(e)}), 500

@app.route('/api/reporte-inventario', methods=['GET'])
def api_reporte_inventario():
    try:
        reporte = simulador.generar_reporte_inventario()
        
        reporte['generado_en'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        reporte['modo_simulacion'] = True
        
        return jsonify(reporte)
    except Exception as e:
        print(f"❌ Error en api_reporte_inventario: {e}")
        return jsonify({"error": "Error generando reporte de inventario", "detalles": str(e)}), 500

@app.route('/api/sistema/estado', methods=['GET'])
def api_sistema_estado():
    """API que devuelve estado de todos los servicios"""
    try:
        # Actualizar estado de Django
        config.DJANGO_DISPONIBLE = config._verificar_django()
        
        # Verificar servicios
        servicios = [
            {
                'nombre': 'Flask Web',
                'url': config.FLASK_URL,
                'estado': 'online',
                'detalle': 'Sistema principal funcionando'
            },
            {
                'nombre': 'Django Reportes',
                'url': config.DJANGO_URL,
                'estado': 'online' if config.DJANGO_DISPONIBLE else 'offline',
                'detalle': 'Disponible' if config.DJANGO_DISPONIBLE else 'No responde'
            },
            {
                'nombre': 'Base de Datos',
                'url': f'file://{config.DB_PATH}',
                'estado': 'online' if os.path.exists(config.DB_PATH) else 'offline',
                'detalle': config.DB_PATH if os.path.exists(config.DB_PATH) else 'Archivo no encontrado'
            }
        ]
        
        return jsonify({
            "estado": "SIMULACION",
            "mensaje": "Sistema funcionando en modo simulación",
            "timestamp": datetime.now().isoformat(),
            "version": "2.4.0",
            "config": {
                "local_ip": config.LOCAL_IP,
                "flask_url": config.FLASK_URL,
                "django_url": config.DJANGO_URL,
                "django_disponible": config.DJANGO_DISPONIBLE
            },
            "servicios": servicios
        })
    except Exception as e:
        return jsonify({"estado": "ERROR", "mensaje": str(e)}), 500

# ==================== MANEJADOR DE ERRORES ====================
@app.errorhandler(404)
def pagina_no_encontrada(e):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>404 - No encontrado</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 50px;
                text-align: center;
                background: #f8f9fa;
            }}
            .error {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                max-width: 600px;
                margin: 0 auto;
            }}
            h1 {{ color: #dc3545; }}
            .btn {{
                display: inline-block;
                padding: 10px 20px;
                background: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="error">
            <h1>404 - Página no encontrada</h1>
            <p>La página que buscas no existe.</p>
            <a href="/" class="btn">Volver al inicio</a>
        </div>
    </body>
    </html>
    """, 404

@app.errorhandler(500)
def error_interno(e):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>500 - Error interno</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 50px;
                text-align: center;
                background: #f8f9fa;
            }}
            .error {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                max-width: 600px;
                margin: 0 auto;
            }}
            h1 {{ color: #dc3545; }}
            .btn {{
                display: inline-block;
                padding: 10px 20px;
                background: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="error">
            <h1>500 - Error interno del servidor</h1>
            <p>Ha ocurrido un error en el servidor.</p>
            <p><strong>Detalles:</strong> {str(e)}</p>
            <a href="/" class="btn">Volver al inicio</a>
            <a href="/reportes" class="btn">Ir a Reportes</a>
        </div>
    </body>
    </html>
    """, 500

# ==================== EJECUCIÓN ====================
if __name__ == '__main__':
    # Eliminar variable de entorno problemática si existe
    if 'WERKZEUG_SERVER_FD' in os.environ:
        del os.environ['WERKZEUG_SERVER_FD']
    
    # Deshabilitar logs de Flask/Werkzeug
    import logging
    log = logging.getLogger('werkzeug')
    log.disabled = True
    
    print("\n" + "="*60)
    print("🌐 CARNE FELIZ - SISTEMA WEB COMPLETO v2.4.0")
    print("="*60)
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y')}")
    print(f"🕒 Hora: {datetime.now().strftime('%H:%M:%S')}")
    print(f"🌐 IP Local detectada: {config.LOCAL_IP}")
    print(f"🔧 Modo: SIMULACIÓN")
    print(f"🔌 Puerto: {config.FLASK_PORT}")
    print(f"📊 Django disponible: {'✅ SI' if config.DJANGO_DISPONIBLE else '❌ NO'}")
    print("\n🌍 URLs del sistema:")
    print(f"   • Dashboard: {config.FLASK_URL}")
    print(f"   • Reportes Django: {config.DJANGO_URL}/reportes")
    print(f"   • Caja: {config.FLASK_URL}/caja")
    print(f"   • Ventas: {config.FLASK_URL}/ventas")
    print("\n📡 Accede desde cualquier dispositivo en tu red usando:")
    print(f"   {config.FLASK_URL}")
    print("\n📋 Para salir: Ctrl+C")
    print("="*60 + "\n")
    
    # Verificar si Django está ejecutándose
    if not config.DJANGO_DISPONIBLE:
        print("⚠️  ADVERTENCIA: Django no está disponible.")
        print(f"   Para usar reportes, ejecuta Django en: {config.DJANGO_URL}")
        print(f"   Comando: cd django_report && python manage.py runserver {config.LOCAL_IP}:5000")
    
    try:
        # Ejecutar servidor Flask
        app.run(
            host='0.0.0.0',
            port=config.FLASK_PORT,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido. ¡Hasta pronto!")
    except Exception as e:
        print(f"\n❌ Error al ejecutar el servidor: {e}")
        sys.exit(1)