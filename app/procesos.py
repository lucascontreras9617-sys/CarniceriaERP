# app/procesos.py (VERSIÓN CORREGIDA Y ORGANIZADA)
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from app.infraestructura.persistence.orm.modelos import Cliente
from app.infraestructura.persistence.orm.modelos import Venta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar solo lo que existe
try:
    from .modelos import ProductoElaborado, Cliente, Caja, Venta, Gasto
    from .persistencia import db_manager
    IMPORT_SUCCESS = True
    logger.info("✅ Importación de modelos exitosa")
except ImportError as e:
    logger.error(f"⚠️ Algunos imports fallaron en procesos.py: {e}")
    IMPORT_SUCCESS = False

# ============================================================================
# CLASES DE GESTIÓN
# ============================================================================

class AlertaStockManager:
    """Gestiona alertas de stock (versión simplificada)."""
    
    def __init__(self):
        self.UMBRALES = {
            "CRITICO": 2.0,      # Menos de 2 kg
            "BAJO": 5.0,         # Menos de 5 kg  
            "NORMAL": 10.0       # Menos de 10 kg
        }
    
    def generar_alertas(self, umbral_personalizado: Optional[float] = None) -> List[dict]:
        """Revisa el stock actual de cada producto contra su umbral."""
        logger.info("🔔 Revisión diaria de stock (alertas)")
        
        if not IMPORT_SUCCESS:
            logger.warning("Módulo no disponible - retornando lista vacía")
            return []
        
        alertas = []
        try:
            with db_manager.get_session() as session:
                productos = session.query(ProductoElaborado).all()
                
                for producto in productos:
                    if not producto.activo:
                        continue
                    
                    # Determinar umbral
                    umbral = umbral_personalizado or self.UMBRALES["BAJO"]
                    stock = producto.stock_actual if producto.stock_actual is not None else 0.0
                    
                    # Clasificar alerta
                    if stock <= self.UMBRALES["CRITICO"]:
                        tipo = "CRÍTICO"
                        icono = "🚨"
                    elif stock <= self.UMBRALES["BAJO"]:
                        tipo = "BAJO"
                        icono = "⚠️"
                    elif stock <= self.UMBRALES["NORMAL"]:
                        tipo = "NORMAL"
                        icono = "📉"
                    else:
                        continue  # Stock suficiente, no generar alerta
                    
                    alerta = {
                        'id_producto': producto.id,
                        'producto': producto.nombre,
                        'tipo_alerta': tipo,
                        'stock_actual': round(stock, 2),
                        'stock_minimo': round(umbral, 2),
                        'diferencia': round(umbral - stock, 2),
                        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'prioridad': 1 if tipo == "CRÍTICO" else 2 if tipo == "BAJO" else 3
                    }
                    alertas.append(alerta)
                    
                    logger.info(f"{icono} {tipo}: {producto.nombre} ({stock:.2f} kg)")
            
            if not alertas:
                logger.info("✅ Inventario OK. No se encontraron alertas de bajo stock.")
            
            # Ordenar por prioridad
            alertas.sort(key=lambda x: x['prioridad'])
            
        except Exception as e:
            logger.error(f"Error generando alertas: {e}", exc_info=True)
        
        return alertas
    
    def generar_reporte_detallado(self) -> Dict[str, Any]:
        """Genera un reporte detallado del estado del inventario."""
        reporte = {
            'fecha_generacion': datetime.now().isoformat(),
            'total_productos': 0,
            'productos_criticos': 0,
            'productos_bajos': 0,
            'productos_normales': 0,
            'valor_total_inventario': 0.0,
            'alertas': []
        }
        
        if not IMPORT_SUCCESS:
            return reporte
        
        try:
            with db_manager.get_session() as session:
                productos = session.query(ProductoElaborado).filter_by(activo=True).all()
                reporte['total_productos'] = len(productos)
                
                for producto in productos:
                    stock = producto.stock_actual or 0.0
                    precio = producto.precio_venta or 0.0
                    valor = stock * precio
                    reporte['valor_total_inventario'] += valor
                    
                    if stock <= self.UMBRALES["CRITICO"]:
                        reporte['productos_criticos'] += 1
                    elif stock <= self.UMBRALES["BAJO"]:
                        reporte['productos_bajos'] += 1
                    else:
                        reporte['productos_normales'] += 1
                
                reporte['valor_total_inventario'] = round(reporte['valor_total_inventario'], 2)
                reporte['alertas'] = self.generar_alertas()
                
        except Exception as e:
            logger.error(f"Error generando reporte detallado: {e}")
        
        return reporte


class ReporteManager:
    """Generación de reportes clave."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ReporteManager")
    
    def reporte_margen_por_corte(self, margen_minimo_pct: float = 25.0) -> List[dict]:
        """Reporta cortes cuyo margen bruto esté por debajo del mínimo."""
        self.logger.info(f"📊 Generando reporte de márgenes (mínimo: {margen_minimo_pct}%)")
        
        if not IMPORT_SUCCESS:
            self.logger.warning("Módulo no disponible")
            return []
        
        productos_bajo_margen = []
        try:
            with db_manager.get_session() as session:
                productos = session.query(ProductoElaborado).filter_by(activo=True).all()
                
                for producto in productos:
                    costo = producto.costo_elaboracion or 0.0
                    precio = producto.precio_venta or 0.0
                    
                    if costo > 0 and precio > 0:
                        margen_bruto = precio - costo
                        margen_pct = (margen_bruto / precio) * 100 if precio > 0 else 0
                        
                        if margen_pct < margen_minimo_pct:
                            producto_info = {
                                'id': producto.id,
                                'nombre': producto.nombre,
                                'costo_kg': round(costo, 2),
                                'precio_kg': round(precio, 2),
                                'margen_bruto': round(margen_bruto, 2),
                                'margen_pct': round(margen_pct, 2),
                                'stock_actual': round(producto.stock_actual or 0, 2),
                                'categoria': getattr(producto, 'categoria', 'NO DEFINIDA')
                            }
                            productos_bajo_margen.append(producto_info)
                            
                            self.logger.warning(
                                f"⚠️ Margen bajo: {producto.nombre} - "
                                f"{margen_pct:.1f}% (${precio:.2f} - ${costo:.2f})"
                            )
                
                if not productos_bajo_margen:
                    self.logger.info("✅ Todos los productos tienen márgenes saludables")
                
        except Exception as e:
            self.logger.error(f"Error en reporte margen: {e}", exc_info=True)
        
        return productos_bajo_margen
    
    def reporte_rotacion_productos(self, dias_periodo: int = 30) -> List[dict]:
        """Genera reporte de rotación de productos."""
        self.logger.info(f"📈 Generando reporte de rotación ({dias_periodo} días)")
        
        # En una implementación real, aquí se consultarían las ventas
        # Este es un esqueleto para la funcionalidad
        reporte = []
        
        if not IMPORT_SUCCESS:
            return reporte
        
        try:
            fecha_inicio = datetime.now() - timedelta(days=dias_periodo)
            
            with db_manager.get_session() as session:
                productos = session.query(ProductoElaborado).filter_by(activo=True).all()
                
                for producto in productos:
                    # En una implementación completa, calcularías:
                    # 1. Ventas del período
                    # 2. Stock promedio
                    # 3. Rotación = Ventas / Stock promedio
                    
                    rotacion_estimada = 0.0  # Placeholder
                    
                    item_reporte = {
                        'producto': producto.nombre,
                        'stock_actual': round(producto.stock_actual or 0, 2),
                        'rotacion_estimada': rotacion_estimada,
                        'categoria': getattr(producto, 'categoria', 'N/A')
                    }
                    reporte.append(item_reporte)
            
            # Ordenar por rotación (descendente)
            reporte.sort(key=lambda x: x['rotacion_estimada'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error en reporte rotación: {e}")
        
        return reporte


class CreditoManager:
    """Gestiona alertas de cuentas por cobrar."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.CreditoManager")
    
    def generar_reporte_vencidas(self, dias_vencimiento: int = 30) -> List[dict]:
        """Revisa ventas a crédito para identificar aquellas que están vencidas."""
        self.logger.info(f"💳 Revisando créditos vencidos (> {dias_vencimiento} días)")
        
        if not IMPORT_SUCCESS:
            self.logger.warning("Módulo no disponible")
            return []
        
        cuentas_vencidas = []
        try:
            fecha_limite = datetime.now() - timedelta(days=dias_vencimiento)
            
            # En una implementación real, consultarías las ventas a crédito
            # que tengan fecha anterior a fecha_limite y estado = 'PENDIENTE'
            
            # Placeholder para la lógica real
            self.logger.info("🔍 Buscando cuentas vencidas...")
            
            # Simulación de datos
            cuentas_vencidas = [
                {
                    'id_venta': 'VENTA-20231215-001',
                    'cliente': 'Cliente Ejemplo S.A.',
                    'monto_total': 1250.50,
                    'saldo_pendiente': 1250.50,
                    'dias_vencido': 45,
                    'fecha_emision': '2023-12-15',
                    'contacto': 'contacto@ejemplo.com'
                }
            ]
            
            if cuentas_vencidas:
                for cuenta in cuentas_vencidas:
                    self.logger.warning(
                        f"⚠️ Cuenta vencida: {cuenta['id_venta']} - "
                        f"Cliente: {cuenta['cliente']} - "
                        f"${cuenta['saldo_pendiente']:.2f} ({cuenta['dias_vencido']} días)"
                    )
            else:
                self.logger.info("✅ Todas las cuentas están al día")
            
        except Exception as e:
            self.logger.error(f"Error revisando créditos vencidos: {e}", exc_info=True)
        
        return cuentas_vencidas
    
    def verificar_limite_global(self, umbral_porcentaje: float = 90.0) -> List[dict]:
        """Revisa qué clientes tienen su saldo pendiente cerca o por encima de su límite."""
        self.logger.info(f"💰 Revisando límites de crédito (> {umbral_porcentaje}%)")
        
        if not IMPORT_SUCCESS:
            self.logger.warning("Módulo no disponible")
            return []
        
        clientes_alerta = []
        try:
            with db_manager.get_session() as session:
                clientes = session.query(Cliente).filter_by(activo=True).all()
                
                for cliente in clientes:
                    limite = cliente.limite_credito or 0.0
                    saldo = cliente.saldo_pendiente or 0.0
                    
                    if limite > 0:
                        porcentaje_uso = (saldo / limite) * 100
                        
                        if porcentaje_uso >= umbral_porcentaje:
                            alerta = {
                                'id_cliente': cliente.id,
                                'cliente': cliente.nombre,
                                'limite_credito': round(limite, 2),
                                'saldo_actual': round(saldo, 2),
                                'porcentaje_uso': round(porcentaje_uso, 2),
                                'contacto': cliente.telefono or cliente.email or 'No disponible',
                                'fecha_revision': datetime.now().strftime('%Y-%m-%d')
                            }
                            clientes_alerta.append(alerta)
                            
                            nivel = "🚨 PELIGRO" if porcentaje_uso >= 100 else "⚠️ ALERTA"
                            self.logger.warning(
                                f"{nivel}: {cliente.nombre} - "
                                f"Límite usado: {porcentaje_uso:.1f}% "
                                f"(${saldo:.2f} / ${limite:.2f})"
                            )
            
            if not clientes_alerta:
                self.logger.info("✅ Todos los clientes están dentro de sus límites")
            
        except Exception as e:
            self.logger.error(f"Error verificando límites: {e}", exc_info=True)
        
        return clientes_alerta


class CuentaPorCobrar:
    """Representa una cuenta por cobrar a un cliente."""
    
    def __init__(self, id_venta: str, cliente: Cliente, monto: float, 
                 dias_credito: int = 30, descripcion: str = ""):
        self.id_venta = id_venta
        self.cliente = cliente
        self.monto_total = float(monto)
        self.dias_credito = int(dias_credito)
        self.descripcion = descripcion
        
        self.fecha_emision = datetime.now()
        self.fecha_vencimiento = self.fecha_emision + timedelta(days=self.dias_credito)
        
        self.estado = 'PENDIENTE'  # PENDIENTE, PARCIAL, PAGADA, VENCIDA
        self.monto_pagado = 0.0
        self.saldo_pendiente = self.monto_total
        
        self.historial_pagos = []
        self.dias_retraso = 0
        
        self.logger = logging.getLogger(f"{__name__}.CuentaPorCobrar.{id_venta}")
        self.logger.info(f"Nueva cuenta creada: {self}")
    
    def verificar_vencimiento(self) -> tuple:
        """Verifica si la cuenta está vencida y calcula días de retraso."""
        hoy = datetime.now()
        vencida = hoy > self.fecha_vencimiento
        
        if vencida:
            self.dias_retraso = (hoy - self.fecha_vencimiento).days
            if self.estado != 'PAGADA':
                self.estado = 'VENCIDA'
                self.logger.warning(f"Cuenta vencida hace {self.dias_retraso} días")
        
        return vencida, self.dias_retraso
    
    def registrar_pago(self, monto_pago: float, metodo: str = "EFECTIVO", 
                      referencia: str = "") -> bool:
        """Registra un pago parcial o total."""
        try:
            monto = float(monto_pago)
            
            # Validaciones
            if monto <= 0:
                self.logger.error("Monto de pago debe ser mayor a 0")
                return False
            
            if monto > self.saldo_pendiente:
                self.logger.warning(
                    f"Pago (${monto:.2f}) excede saldo pendiente (${self.saldo_pendiente:.2f}). "
                    f"Ajustando a saldo pendiente."
                )
                monto = self.saldo_pendiente
            
            # Registrar pago
            self.monto_pagado += monto
            self.saldo_pendiente -= monto
            
            # Registrar en historial
            pago = {
                'fecha': datetime.now(),
                'monto': monto,
                'metodo': metodo,
                'referencia': referencia,
                'saldo_anterior': self.saldo_pendiente + monto,
                'saldo_nuevo': self.saldo_pendiente
            }
            self.historial_pagos.append(pago)
            
            # Actualizar estado
            if self.saldo_pendiente <= 0.01:  # Tolerancia pequeña
                self.estado = 'PAGADA'
                self.logger.info(f"✅ Cuenta PAGADA COMPLETAMENTE")
                
                # Si estaba vencida, actualizar días de retraso al momento del pago
                if hasattr(self, 'fecha_vencimiento'):
                    hoy = datetime.now()
                    if hoy > self.fecha_vencimiento:
                        self.dias_retraso = (hoy - self.fecha_vencimiento).days
            elif self.monto_pagado > 0:
                self.estado = 'PARCIAL'
                self.logger.info(
                    f"✅ Pago parcial registrado: ${monto:.2f}. "
                    f"Saldo restante: ${self.saldo_pendiente:.2f}"
                )
            
            # Actualizar saldo del cliente si es posible
            if hasattr(self.cliente, 'saldo_pendiente'):
                self.cliente.saldo_pendiente = max(0, self.cliente.saldo_pendiente - monto)
            
            return True
            
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error registrando pago: {e}")
            return False
    
    def generar_recibo_pago(self) -> Dict[str, Any]:
        """Genera un recibo del pago más reciente."""
        if not self.historial_pagos:
            return {}
        
        ultimo_pago = self.historial_pagos[-1]
        return {
            'id_cuenta': self.id_venta,
            'cliente': self.cliente.nombre if hasattr(self.cliente, 'nombre') else 'Cliente',
            'fecha_pago': ultimo_pago['fecha'].strftime('%Y-%m-%d %H:%M'),
            'monto_pagado': ultimo_pago['monto'],
            'metodo_pago': ultimo_pago['metodo'],
            'referencia': ultimo_pago['referencia'],
            'saldo_anterior': ultimo_pago['saldo_anterior'],
            'saldo_nuevo': ultimo_pago['saldo_nuevo'],
            'estado_actual': self.estado
        }
    
    def calcular_interes_mora(self, tasa_diaria: float = 0.05) -> float:
        """Calcula intereses por mora si la cuenta está vencida."""
        vencida, dias = self.verificar_vencimiento()
        
        if vencida and self.saldo_pendiente > 0:
            interes = self.saldo_pendiente * (tasa_diaria / 100) * dias
            self.logger.info(f"Interés por mora ({dias} días): ${interes:.2f}")
            return round(interes, 2)
        
        return 0.0
    
    def __str__(self) -> str:
        vencida, dias = self.verificar_vencimiento()
        
        estado_detalle = f"{self.estado}"
        if vencida and self.estado != 'PAGADA':
            estado_detalle += f" ({dias} días de retraso)"
        
        return (
            f"Cuenta #{self.id_venta} - "
            f"Cliente: {getattr(self.cliente, 'nombre', 'N/A')} - "
            f"Monto: ${self.monto_total:.2f} - "
            f"Pagado: ${self.monto_pagado:.2f} - "
            f"Saldo: ${self.saldo_pendiente:.2f} - "
            f"Estado: {estado_detalle} - "
            f"Vence: {self.fecha_vencimiento.strftime('%d/%m/%Y')}"
        )


class ProcesoDeDespiece:
    """Gestiona el proceso de despiece de carne."""
    
    def __init__(self, lote: Any, cantidad_a_procesar: float):
        self.lote = lote
        self.cantidad_a_procesar = float(cantidad_a_procesar)
        self.productos_generados = []
        self.fecha_proceso = datetime.now()
        self.merma_total = 0.0
        self.rendimiento_total = 0.0
        self.eficiencia = 0.0
        
        self.logger = logging.getLogger(f"{__name__}.ProcesoDespiece")
        
        # Información del lote (con verificaciones seguras)
        self.nombre_lote = getattr(
            getattr(lote, 'materia_prima', None), 'nombre', 'Desconocido'
        ) if hasattr(lote, 'materia_prima') else 'Desconocido'
        
        self.logger.info(
            f"🔪 Nuevo proceso de despiece iniciado - "
            f"Lote: {self.nombre_lote} - "
            f"Cantidad: {self.cantidad_a_procesar:.2f} kg"
        )
    
    def validar_lote(self) -> bool:
        """Valida que el lote tenga los atributos necesarios."""
        atributos_requeridos = ['peso_restante']
        
        for attr in atributos_requeridos:
            if not hasattr(self.lote, attr):
                self.logger.error(f"Lote no tiene atributo requerido: {attr}")
                return False
        
        return True
    
    def ejecutar_proceso(self, rendimiento: Dict[Any, float], 
                        producto_merma: Optional[Any] = None) -> bool:
        """Ejecuta el despiece según el rendimiento especificado."""
        self.logger.info("🔪 Ejecutando proceso de despiece")
        
        # Validar lote
        if not self.validar_lote():
            return False
        
        # Verificar que haya suficiente materia prima
        peso_disponible = getattr(self.lote, 'peso_restante', 0.0)
        
        if peso_disponible < self.cantidad_a_procesar:
            self.logger.error(
                f"Stock insuficiente en lote. "
                f"Disponible: {peso_disponible:.2f} kg, "
                f"Necesario: {self.cantidad_a_procesar:.2f} kg"
            )
            return False
        
        # Calcular total del rendimiento
        try:
            total_rendimiento = sum(float(v) for v in rendimiento.values())
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error calculando rendimiento: {e}")
            return False
        
        # Calcular merma
        self.merma_total = self.cantidad_a_procesar - total_rendimiento
        self.rendimiento_total = total_rendimiento
        
        # Calcular eficiencia
        if self.cantidad_a_procesar > 0:
            self.eficiencia = (total_rendimiento / self.cantidad_a_procesar) * 100
        else:
            self.eficiencia = 0.0
        
        # Verificar consistencia
        if total_rendimiento > self.cantidad_a_procesar:
            self.logger.warning(
                f"⚠️ Rendimiento ({total_rendimiento:.2f} kg) > "
                f"Cantidad procesada ({self.cantidad_a_procesar:.2f} kg)"
            )
        elif self.merma_total < 0:
            self.logger.warning(f"⚠️ Merma negativa ({self.merma_total:.2f} kg)")
        
        # Descontar del lote
        self.lote.peso_restante = max(0.0, peso_disponible - self.cantidad_a_procesar)
        
        # Mostrar resumen
        self._mostrar_resumen()
        
        # Generar productos
        for producto, cantidad in rendimiento.items():
            if not self._procesar_producto(producto, cantidad):
                self.logger.warning(f"Error procesando producto: {producto}")
                continue
        
        # Manejar merma si se especifica
        if self.merma_total > 0 and producto_merma is not None:
            self._procesar_merma(producto_merma)
        
        # Mostrar estado final
        self._mostrar_estado_final()
        
        self.logger.info("✅ Proceso de despiece completado exitosamente")
        return True
    
    def _procesar_producto(self, producto: Any, cantidad: float) -> bool:
        """Procesa un producto individual."""
        try:
            cantidad_float = float(cantidad)
            
            # Aumentar stock del producto
            if hasattr(producto, 'stock_actual'):
                stock_actual = producto.stock_actual or 0.0
                producto.stock_actual = stock_actual + cantidad_float
            
            # Calcular costo asignado
            costo_kg = getattr(self.lote, 'costo_real_kg', 0.0)
            costo_asignado = cantidad_float * costo_kg
            
            # Registrar producto generado
            producto_info = {
                'producto': getattr(producto, 'nombre', 'Desconocido'),
                'id_producto': getattr(producto, 'id', None),
                'cantidad': round(cantidad_float, 3),
                'costo_asignado': round(costo_asignado, 2),
                'costo_kg': round(costo_kg, 2),
                'tipo': getattr(producto, 'tipo', 'GENERAL'),
                'categoria': getattr(producto, 'categoria', 'NO DEFINIDA')
            }
            
            self.productos_generados.append(producto_info)
            
            self.logger.info(
                f"  ✅ Generado: {cantidad_float:.3f} kg de "
                f"{getattr(producto, 'nombre', 'Producto')}"
            )
            
            return True
            
        except (ValueError, TypeError, AttributeError) as e:
            self.logger.error(f"Error procesando producto: {e}")
            return False
    
    def _procesar_merma(self, producto_merma: Any) -> bool:
        """Procesa la merma del despiece."""
        try:
            if hasattr(producto_merma, 'stock_actual'):
                stock_actual = producto_merma.stock_actual or 0.0
                producto_merma.stock_actual = stock_actual + self.merma_total
                
                self.logger.info(
                    f"  📦 Merma registrada: {self.merma_total:.3f} kg de "
                    f"{getattr(producto_merma, 'nombre', 'Merma')}"
                )
                return True
                
        except AttributeError as e:
            self.logger.error(f"Error procesando merma: {e}")
        
        return False
    
    def _mostrar_resumen(self) -> None:
        """Muestra un resumen del proceso."""
        self.logger.info("\n📊 RESUMEN DEL PROCESO:")
        self.logger.info(f"   - Cantidad procesada: {self.cantidad_a_procesar:.3f} kg")
        self.logger.info(f"   - Productos generados: {self.rendimiento_total:.3f} kg")
        self.logger.info(f"   - Merma total: {self.merma_total:.3f} kg")
        self.logger.info(f"   - Eficiencia: {self.eficiencia:.1f}%")
        
        if self.merma_total > 0:
            porcentaje_merma = (self.merma_total / self.cantidad_a_procesar) * 100
            self.logger.info(f"   - Porcentaje merma: {porcentaje_merma:.1f}%")
    
    def _mostrar_estado_final(self) -> None:
        """Muestra el estado final del lote."""
        if hasattr(self.lote, 'peso_restante'):
            peso_restante = self.lote.peso_restante
            peso_inicial = getattr(self.lote, 'peso_inicial', self.cantidad_a_procesar + peso_restante)
            
            if peso_inicial > 0:
                porcentaje_usado = ((peso_inicial - peso_restante) / peso_inicial) * 100
                
                self.logger.info("\n📦 ESTADO FINAL DEL LOTE:")
                self.logger.info(f"   - Peso restante: {peso_restante:.3f} kg")
                self.logger.info(f"   - Porcentaje usado: {porcentaje_usado:.1f}%")
    
    def get_resumen(self) -> Dict[str, Any]:
        """Devuelve un resumen estructurado del proceso."""
        total_productos = sum(p['cantidad'] for p in self.productos_generados)
        total_costo = sum(p['costo_asignado'] for p in self.productos_generados)
        
        return {
            'fecha': self.fecha_proceso.strftime('%Y-%m-%d %H:%M:%S'),
            'lote': self.nombre_lote,
            'cantidad_procesada': round(self.cantidad_a_procesar, 3),
            'total_productos': round(total_productos, 3),
            'merma': round(self.merma_total, 3),
            'eficiencia': round(self.eficiencia, 2),
            'costo_total': round(total_costo, 2),
            'productos_generados': self.productos_generados,
            'peso_restante_lote': round(getattr(self.lote, 'peso_restante', 0.0), 3)
        }
    
    def generar_reporte_calidad(self) -> Dict[str, Any]:
        """Genera un reporte de calidad del proceso."""
        resumen = self.get_resumen()
        
        # Evaluar calidad basada en eficiencia
        if self.eficiencia >= 90:
            calidad = "EXCELENTE"
            color = "🟢"
        elif self.eficiencia >= 80:
            calidad = "BUENA"
            color = "🟡"
        elif self.eficiencia >= 70:
            calidad = "ACEPTABLE"
            color = "🟠"
        else:
            calidad = "MEJORABLE"
            color = "🔴"
        
        reporte = {
            **resumen,
            'calidad_proceso': calidad,
            'color_calidad': color,
            'observaciones': self._generar_observaciones(),
            'recomendaciones': self._generar_recomendaciones()
        }
        
        return reporte
    
    def _generar_observaciones(self) -> List[str]:
        """Genera observaciones basadas en los resultados."""
        observaciones = []
        
        if self.eficiencia < 70:
            observaciones.append("Eficiencia baja. Revisar técnica de despiece.")
        
        if self.merma_total > (self.cantidad_a_procesar * 0.15):  # Más del 15% de merma
            observaciones.append("Merma excesiva. Verificar calidad de materia prima.")
        
        if not observaciones:
            observaciones.append("Proceso dentro de parámetros normales.")
        
        return observaciones
    
    def _generar_recomendaciones(self) -> List[str]:
        """Genera recomendaciones para mejorar el proceso."""
        recomendaciones = []
        
        if self.eficiencia < 80:
            recomendaciones.append("Capacitar al personal en técnicas de despiece.")
            recomendaciones.append("Revisar y afilar herramientas de corte.")
        
        if len(self.productos_generados) < 3:
            recomendaciones.append("Diversificar productos del despiece.")
        
        if not recomendaciones:
            recomendaciones.append("Mantener procedimientos actuales.")
        
        return recomendaciones
    
    def __str__(self) -> str:
        return (
            f"ProcesoDespiece[{self.nombre_lote}] - "
            f"Procesado: {self.cantidad_a_procesar:.2f} kg - "
            f"Eficiencia: {self.eficiencia:.1f}% - "
            f"Merma: {self.merma_total:.2f} kg"
        )


# ============================================================================
# FUNCIONES DE CONVENIENCIA
# ============================================================================

def ejecutar_revision_diaria() -> Dict[str, Any]:
    """Ejecuta todas las revisiones diarias del sistema."""
    logger.info("\n" + "="*60)
    logger.info("🔍 EJECUTANDO REVISIÓN DIARIA DEL SISTEMA")
    logger.info("="*60)
    
    resultado = {
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'alertas_stock': [],
        'margenes_bajos': [],
        'creditos_vencidos': [],
        'limites_excedidos': [],
        'resumen': {}
    }
    
    # 1. Alertas de stock
    stock_manager = AlertaStockManager()
    resultado['alertas_stock'] = stock_manager.generar_alertas()
    
    # 2. Reporte de márgenes
    reporte_manager = ReporteManager()
    resultado['margenes_bajos'] = reporte_manager.reporte_margen_por_corte()
    
    # 3. Créditos vencidos
    credito_manager = CreditoManager()
    resultado['creditos_vencidos'] = credito_manager.generar_reporte_vencidas()
    
    # 4. Límites de crédito
    resultado['limites_excedidos'] = credito_manager.verificar_limite_global()
    
    # Resumen estadístico
    resultado['resumen'] = {
        'total_alertas': (
            len(resultado['alertas_stock']) +
            len(resultado['margenes_bajos']) +
            len(resultado['creditos_vencidos']) +
            len(resultado['limites_excedidos'])
        ),
        'alertas_criticas': len([a for a in resultado['alertas_stock'] 
                                if a.get('tipo_alerta') == 'CRÍTICO']),
        'status': 'OK' if resultado['resumen']['total_alertas'] == 0 else 'CON ALERTAS'
    }
    
    logger.info(f"\n📋 RESUMEN: {resultado['resumen']['total_alertas']} alertas encontradas")
    logger.info("="*60)
    
    return resultado


def simular_venta_rapida():
    """Simula una venta rápida para pruebas."""
    logger.info("\n🛒 SIMULANDO VENTA RÁPIDA")
    
    try:
        # Crear cliente simulado
        class ClienteSimulado:
            def __init__(self):
                self.id = 999
                self.nombre = "CLIENTE PRUEBA"
                self.saldo_pendiente = 0.0
                self.limite_credito = 10000.0
                self.activo = True
        
        # Crear empleado simulado
        class EmpleadoSimulado:
            def __init__(self):
                self.id = 1
                self.nombre = "EMPLEADO PRUEBA"
                self.comision_pct = 0.05  # 5% de comisión
        
        # Crear producto simulado
        class ProductoSimulado:
            def __init__(self, nombre, precio, stock):
                self.id = 1
                self.nombre = nombre
                self.precio_venta = precio
                self.stock_actual = stock
                self.activo = True
        
        cliente = ClienteSimulado()
        empleado = EmpleadoSimulado()
        
        # Productos de prueba
        productos = [
            ProductoSimulado("LOMO FINO", 850.0, 15.5),
            ProductoSimulado("BIFE DE CHORIZO", 920.0, 8.2),
            ProductoSimulado("ASADO", 780.0, 12.0)
        ]
        
        # Crear venta
        venta = Venta(
            cliente=cliente,
            empleado=empleado,
            tipo_pago='EFECTIVO'
        )
        
        # Agregar items
        venta.agregar_item(productos[0], 1.5, productos[0].precio_venta)
        venta.agregar_item(productos[1], 0.8, productos[1].precio_venta)
        venta.agregar_item(productos[2], 2.0, productos[2].precio_venta)
        
        # Cerrar venta
        venta.cerrar_venta()
        
        logger.info("✅ Simulación de venta completada")
        
    except Exception as e:
        logger.error(f"Error en simulación: {e}")


# ============================================================================
# PUNTO DE ENTRADA PARA PRUEBAS
# ============================================================================

if __name__ == "__main__":
    """Punto de entrada para pruebas directas."""
    print("\n" + "="*60)
    print("🧪 MÓDULO DE PROCESOS - MODO PRUEBA")
    print("="*60)
    
    # Ejecutar revisión diaria
    resultado = ejecutar_revision_diaria()
    
    print(f"\n📊 Resultado revisión:")
    print(f"   - Alertas stock: {len(resultado['alertas_stock'])}")
    print(f"   - Márgenes bajos: {len(resultado['margenes_bajos'])}")
    print(f"   - Créditos vencidos: {len(resultado['creditos_vencidos'])}")
    print(f"   - Límites excedidos: {len(resultado['limites_excedidos'])}")
    print(f"   - Status: {resultado['resumen']['status']}")
    
    # Simular venta si no hay import errors
    if IMPORT_SUCCESS:
        simular_venta_rapida()
    
    print("\n✅ Pruebas completadas")
    print("="*60)