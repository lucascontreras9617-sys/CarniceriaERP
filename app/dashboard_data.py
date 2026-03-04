# app/dashboard_data.py (NUEVO - PARA LA WEB)
from datetime import datetime, date, timedelta
from typing import Dict, List, Any
from .persistencia import db_manager
from .caja import ControlCaja
from .procesos import ReporteManager, AlertaStockManager, CreditoManager

class DashboardData:
    """Genera datos estructurados para el dashboard web."""
    
    @staticmethod
    def obtener_dashboard_principal() -> Dict:
        """Obtiene todos los datos para el dashboard principal."""
        try:
            # 1. Estado de caja
            estado_caja = ControlCaja.obtener_estado_caja()
            
            # 2. Alertas de stock
            alerta_manager = AlertaStockManager()
            alertas_stock = alerta_manager.generar_alertas()
            
            # 3. Ventas del día
            ventas_hoy = DashboardData.obtener_ventas_hoy()
            
            # 4. Productos más vendidos
            productos_top = DashboardData.obtener_productos_top()
            
            # 5. Alertas de crédito
            credito_manager = CreditoManager()
            alertas_credito = credito_manager.verificar_limite_global()
            cuentas_vencidas = credito_manager.generar_reporte_vencidas()
            
            # 6. Margen de productos
            reporte_manager = ReporteManager()
            alertas_margen = reporte_manager.reporte_margen_por_corte()
            
            # 7. Resumen financiero
            resumen_financiero = DashboardData.obtener_resumen_financiero()
            
            # 8. Movimientos recientes
            movimientos = ControlCaja.obtener_movimientos_dia()
            
            return {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'estado_caja': estado_caja,
                'ventas_hoy': ventas_hoy,
                'productos_top': productos_top[:5],  # Solo top 5
                'movimientos_recientes': movimientos[:10],  # Solo últimos 10
                'alertas': {
                    'stock': alertas_stock,
                    'credito': alertas_credito,
                    'margen': alertas_margen,
                    'vencidas': cuentas_vencidas
                },
                'resumen_financiero': resumen_financiero,
                'total_alertas': len(alertas_stock) + len(alertas_credito) + len(alertas_margen) + len(cuentas_vencidas)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    @staticmethod
    def obtener_ventas_hoy() -> Dict:
        """Obtiene resumen de ventas del día."""
        with db_manager.get_session() as session:
            from .modelos import VentaDetalle
            
            hoy = date.today()
            
            # Ventas al contado
            ventas_contado = session.query(VentaDetalle).filter(
                VentaDetalle.fecha == hoy,
                VentaDetalle.tipo_pago != 'CREDITO'
            ).all()
            
            # Ventas a crédito
            ventas_credito = session.query(VentaDetalle).filter(
                VentaDetalle.fecha == hoy,
                VentaDetalle.tipo_pago == 'CREDITO'
            ).all()
            
            total_contado = sum(v.subtotal for v in ventas_contado)
            total_credito = sum(v.subtotal for v in ventas_credito)
            total_general = total_contado + total_credito
            
            # Por tipo de pago
            por_tipo_pago = {}
            for venta in ventas_contado + ventas_credito:
                tipo = venta.tipo_pago
                if tipo not in por_tipo_pago:
                    por_tipo_pago[tipo] = 0.0
                por_tipo_pago[tipo] += venta.subtotal
            
            return {
                'total_contado': float(total_contado),
                'total_credito': float(total_credito),
                'total_general': float(total_general),
                'cantidad_ventas': len(ventas_contado) + len(ventas_credito),
                'por_tipo_pago': {k: float(v) for k, v in por_tipo_pago.items()},
                'hora_primera_venta': ventas_contado[0].hora.strftime('%H:%M') if ventas_contado else 'Sin ventas',
                'hora_ultima_venta': ventas_contado[-1].hora.strftime('%H:%M') if ventas_contado else 'Sin ventas'
            }
    
    @staticmethod
    def obtener_productos_top(limite: int = 5) -> List[Dict]:
        """Obtiene los productos más vendidos."""
        with db_manager.get_session() as session:
            from .modelos import VentaDetalle
            from sqlalchemy import func
            
            # Últimos 7 días
            fecha_inicio = date.today() - timedelta(days=7)
            
            resultados = session.query(
                VentaDetalle.producto_nombre,
                func.sum(VentaDetalle.cantidad_kg).label('total_kg'),
                func.sum(VentaDetalle.subtotal).label('total_venta'),
                func.count(VentaDetalle.id).label('cantidad_ventas')
            ).filter(
                VentaDetalle.fecha >= fecha_inicio
            ).group_by(
                VentaDetalle.producto_nombre
            ).order_by(
                func.sum(VentaDetalle.subtotal).desc()
            ).limit(limite).all()
            
            return [{
                'producto': r.producto_nombre,
                'total_kg': float(r.total_kg or 0),
                'total_venta': float(r.total_venta or 0),
                'cantidad_ventas': r.cantidad_ventas or 0
            } for r in resultados]
    
    @staticmethod
    def obtener_resumen_financiero() -> Dict:
        """Obtiene resumen financiero del mes."""
        with db_manager.get_session() as session:
            from .modelos import VentaDetalle, Gasto, Cliente
            from sqlalchemy import func
            
            hoy = date.today()
            inicio_mes = date(hoy.year, hoy.month, 1)
            
            # Ventas del mes (solo contado)
            ventas_mes = session.query(
                func.sum(VentaDetalle.subtotal).label('total_ventas'),
                func.count(VentaDetalle.id).label('cantidad_ventas')
            ).filter(
                VentaDetalle.fecha >= inicio_mes,
                VentaDetalle.tipo_pago != 'CREDITO'
            ).first()
            
            # Gastos del mes
            gastos_mes = session.query(
                func.sum(Gasto.monto).label('total_gastos')
            ).filter(
                Gasto.fecha >= inicio_mes
            ).first()
            
            # Cuentas por cobrar (crédito)
            cuentas_cobrar = session.query(
                func.sum(Cliente.saldo_pendiente).label('total_cobrar')
            ).filter(
                Cliente.tipo == 'MAYORISTA'
            ).first()
            
            total_ventas = float(ventas_mes.total_ventas or 0)
            total_gastos = float(gastos_mes.total_gastos or 0)
            total_cobrar = float(cuentas_cobrar.total_cobrar or 0)
            utilidad = total_ventas - total_gastos
            
            return {
                'mes': hoy.strftime('%B %Y'),
                'total_ventas': total_ventas,
                'total_gastos': total_gastos,
                'utilidad': utilidad,
                'margen': (utilidad / total_ventas * 100) if total_ventas > 0 else 0,
                'cuentas_cobrar': total_cobrar,
                'cantidad_ventas': ventas_mes.cantidad_ventas or 0,
                'dias_transcurridos': (hoy - inicio_mes).days,
                'promedio_diario': total_ventas / ((hoy - inicio_mes).days or 1)
            }

# Función de conveniencia para la web
def generar_datos_dashboard():
    """Genera datos para el dashboard web."""
    return DashboardData.obtener_dashboard_principal()