#!/usr/bin/env python3
"""
Backend API para Carnicería ERP - Puente entre Web y SQLAlchemy
Versión corregida y funcional
"""

import sys
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== IMPORTACIONES SEGURAS ====================

# Intentar importar SQLAlchemy
try:
    from sqlalchemy import func
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    logger.warning("SQLAlchemy no disponible")

# Intentar importar nuestros módulos
try:
    # INTENTO 1: Import relativo (si se ejecuta desde dentro de app/)
    try:
        from persistencia import db_manager
        from modelos import (
            ProductoElaborado, Cliente, Empleado, Caja,
            Venta, VentaItem, Gasto
        )
    except ImportError:
        # INTENTO 2: Import absoluto (si se importa desde fuera de app/)
        from persistencia import db_manager
        from modelos import (
            ProductoElaborado, Cliente, Empleado, Caja,
            Venta, VentaItem, Gasto
        )
    
    MODELS_AVAILABLE = True
    logger.info("✅ Modelos SQLAlchemy importados correctamente")
except ImportError as e:
    MODELS_AVAILABLE = False
    logger.error(f"❌ Error importando modelos: {e}")

# ==================== API DE CAJA ====================

class CajaAPI:
    """API para gestión de caja."""
    
    @staticmethod
    def obtener_estado_caja() -> Dict[str, Any]:
        """Obtiene el estado actual de la caja."""
        if not MODELS_AVAILABLE:
            return {
                "estado": "cerrada",
                "mensaje": "Sistema no inicializado",
                "existe": False,
                "hora_actual": datetime.now().strftime("%H:%M:%S")
            }
        
        try:
            with db_manager.get_session() as session:
                # Buscar caja del día actual
                hoy = date.today()
                caja = session.query(Caja).filter_by(fecha=hoy).first()
                
                if not caja:
                    return {
                        "estado": "cerrada",
                        "mensaje": "Caja no abierta hoy",
                        "hora_actual": datetime.now().strftime("%H:%M:%S"),
                        "existe": False
                    }
                
                if caja.estado != 'abierta':
                    return {
                        "estado": "cerrada",
                        "mensaje": "Caja cerrada",
                        "hora_apertura": caja.hora_apertura.strftime('%H:%M:%S') if caja.hora_apertura else 'N/A',
                        "responsable": caja.responsable or "No asignado",
                        "existe": True,
                        "hora_actual": datetime.now().strftime("%H:%M:%S")
                    }
                
                # Calcular métricas
                ventas_dia = session.query(Venta).filter_by(
                    fecha=hoy,
                    caja_id=caja.id
                ).all()
                
                cantidad_ventas = len(ventas_dia)
                total_ventas = sum(v.total for v in ventas_dia)
                
                # Calcular por tipo de pago
                ventas_efectivo = sum(v.total for v in ventas_dia if v.tipo_pago == 'EFECTIVO')
                ventas_tarjeta = sum(v.total for v in ventas_dia if v.tipo_pago == 'TARJETA')
                
                # Calcular efectivo esperado
                efectivo_esperado = (caja.monto_inicial or 0) + (caja.ventas_efectivo or 0) - (caja.gastos_dia or 0)
                
                return {
                    "estado": caja.estado,
                    "responsable": caja.responsable or "No asignado",
                    "hora_apertura": caja.hora_apertura.strftime('%H:%M:%S') if caja.hora_apertura else 'N/A',
                    "monto_inicial": float(caja.monto_inicial or 0),
                    "ventas_efectivo": float(caja.ventas_efectivo or 0),
                    "ventas_tarjeta": float(caja.ventas_tarjeta or 0),
                    "total_ventas": float(total_ventas),
                    "efectivo_esperado": float(efectivo_esperado),
                    "cantidad_ventas": cantidad_ventas,
                    "gastos_dia": float(caja.gastos_dia or 0),
                    "hora_actual": datetime.now().strftime("%H:%M:%S"),
                    "fecha_actual": hoy.strftime("%Y-%m-%d"),
                    "existe": True,
                    "id_caja": caja.id[:8] if caja.id else 'N/A'
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo estado de caja: {e}")
            return {
                "estado": "error",
                "mensaje": f"Error: {str(e)}",
                "existe": False,
                "hora_actual": datetime.now().strftime("%H:%M:%S")
            }
    
    @staticmethod
    def abrir_caja(monto_inicial: float, responsable: str) -> Dict[str, Any]:
        """Abre la caja del día."""
        if not MODELS_AVAILABLE:
            return {
                "success": False,
                "error": "Sistema de base de datos no disponible"
            }
        
        try:
            monto = float(monto_inicial)
            if monto <= 0:
                return {"success": False, "error": "El monto debe ser mayor a 0"}
            
            with db_manager.get_session() as session:
                hoy = date.today()
                
                # Verificar si ya existe caja hoy
                caja_existente = session.query(Caja).filter_by(fecha=hoy).first()
                
                if caja_existente:
                    if caja_existente.estado == 'abierta':
                        return {
                            "success": False,
                            "error": "Ya existe una caja abierta hoy"
                        }
                    # Reabrir caja cerrada
                    caja_existente.estado = 'abierta'
                    caja_existente.responsable = responsable
                    caja_existente.monto_inicial = monto
                    caja_existente.hora_apertura = datetime.now()
                    caja_existente.hora_cierre = None
                    session.commit()
                    
                    logger.info(f"Caja reabierta: {responsable} con ${monto}")
                    return {
                        "success": True,
                        "mensaje": "Caja reabierta exitosamente",
                        "monto": monto,
                        "responsable": responsable,
                        "caja_id": caja_existente.id[:8]
                    }
                
                # Crear nueva caja
                nueva_caja = Caja(
                    fecha=hoy,
                    estado='abierta',
                    responsable=responsable,
                    monto_inicial=monto,
                    hora_apertura=datetime.now(),
                    ventas_efectivo=0.0,
                    ventas_tarjeta=0.0,
                    gastos_dia=0.0
                )
                
                session.add(nueva_caja)
                session.commit()
                
                logger.info(f"Nueva caja abierta: {responsable} con ${monto}")
                return {
                    "success": True,
                    "mensaje": "Caja abierta exitosamente",
                    "monto": monto,
                    "responsable": responsable,
                    "caja_id": nueva_caja.id[:8]
                }
                
        except ValueError:
            return {"success": False, "error": "Monto inválido"}
        except Exception as e:
            logger.error(f"Error abriendo caja: {e}")
            return {"success": False, "error": f"Error del sistema: {str(e)}"}
    
    @staticmethod
    def cerrar_caja(efectivo_real: float) -> Dict[str, Any]:
        """Cierra la caja del día."""
        if not MODELS_AVAILABLE:
            return {
                "success": False,
                "error": "Sistema de base de datos no disponible"
            }
        
        try:
            efectivo = float(efectivo_real)
            
            with db_manager.get_session() as session:
                hoy = date.today()
                caja = session.query(Caja).filter_by(fecha=hoy, estado='abierta').first()
                
                if not caja:
                    return {
                        "success": False,
                        "error": "No hay caja abierta para cerrar"
                    }
                
                # Calcular efectivo esperado
                efectivo_esperado = (caja.monto_inicial or 0) + (caja.ventas_efectivo or 0) - (caja.gastos_dia or 0)
                diferencia = efectivo - efectivo_esperado
                
                # Actualizar caja
                caja.estado = 'cerrada'
                caja.hora_cierre = datetime.now()
                caja.efectivo_real = efectivo
                
                session.commit()
                
                logger.info(f"Caja cerrada: Efectivo real ${efectivo}, Esperado ${efectivo_esperado}")
                
                return {
                    "success": True,
                    "mensaje": "Caja cerrada exitosamente",
                    "efectivo_esperado": efectivo_esperado,
                    "efectivo_real": efectivo,
                    "diferencia": diferencia,
                    "caja_id": caja.id[:8]
                }
                
        except ValueError:
            return {"success": False, "error": "Monto de efectivo inválido"}
        except Exception as e:
            logger.error(f"Error cerrando caja: {e}")
            return {"success": False, "error": f"Error del sistema: {str(e)}"}
    
    @staticmethod
    def registrar_venta(
        tipo_pago: str,
        monto: float,
        detalles: str = "",
        cliente_nombre: str = ""
    ) -> Dict[str, Any]:
        """Registra una venta en la caja actual."""
        if not MODELS_AVAILABLE:
            return {
                "success": False,
                "error": "Sistema de base de datos no disponible"
            }
        
        try:
            monto_float = float(monto)
            if monto_float <= 0:
                return {"success": False, "error": "El monto debe ser mayor a 0"}
            
            tipo_pago = tipo_pago.upper()
            if tipo_pago not in ['EFECTIVO', 'TARJETA', 'TRANSFERENCIA', 'CREDITO']:
                return {"success": False, "error": "Tipo de pago inválido"}
            
            with db_manager.get_session() as session:
                hoy = date.today()
                
                # Verificar caja abierta
                caja = session.query(Caja).filter_by(fecha=hoy, estado='abierta').first()
                if not caja:
                    return {
                        "success": False,
                        "error": "No hay caja abierta. Debe abrirla primero."
                    }
                
                # Buscar o crear cliente
                cliente_id = None
                if cliente_nombre:
                    cliente = session.query(Cliente).filter_by(nombre=cliente_nombre).first()
                    if not cliente:
                        cliente = Cliente(nombre=cliente_nombre)
                        session.add(cliente)
                        session.flush()
                    cliente_id = cliente.id
                
                # Crear venta
                venta = Venta(
                    fecha=hoy,
                    hora=datetime.now(),
                    tipo_pago=tipo_pago,
                    total=monto_float,
                    caja_id=caja.id,
                    cliente_id=cliente_id
                )
                
                session.add(venta)
                
                # Actualizar caja
                if tipo_pago == 'EFECTIVO':
                    caja.ventas_efectivo = (caja.ventas_efectivo or 0) + monto_float
                elif tipo_pago == 'TARJETA':
                    caja.ventas_tarjeta = (caja.ventas_tarjeta or 0) + monto_float
                
                session.commit()
                
                logger.info(f"Venta registrada: ${monto_float} ({tipo_pago}) - {detalles}")
                
                return {
                    "success": True,
                    "mensaje": "Venta registrada exitosamente",
                    "venta_id": venta.id[:8],
                    "monto": monto_float,
                    "tipo_pago": tipo_pago,
                    "hora": venta.hora.strftime('%H:%M:%S') if venta.hora else 'N/A',
                    "cliente": cliente_nombre or "Cliente general"
                }
                
        except ValueError:
            return {"success": False, "error": "Monto inválido"}
        except Exception as e:
            logger.error(f"Error registrando venta: {e}")
            return {"success": False, "error": f"Error del sistema: {str(e)}"}
    
    @staticmethod
    def registrar_gasto(
        descripcion: str,
        monto: float,
        categoria: str = "GASTO"
    ) -> Dict[str, Any]:
        """Registra un gasto en la caja actual."""
        if not MODELS_AVAILABLE:
            return {
                "success": False,
                "error": "Sistema de base de datos no disponible"
            }
        
        try:
            monto_float = float(monto)
            if monto_float <= 0:
                return {"success": False, "error": "El monto debe ser mayor a 0"}
            
            with db_manager.get_session() as session:
                hoy = date.today()
                
                # Verificar caja abierta
                caja = session.query(Caja).filter_by(fecha=hoy, estado='abierta').first()
                if not caja:
                    return {
                        "success": False,
                        "error": "No hay caja abierta. Debe abrirla primero."
                    }
                
                # Crear gasto
                gasto = Gasto(
                    descripcion=descripcion,
                    monto=monto_float,
                    categoria=categoria,
                    fecha=hoy,
                    caja_id=caja.id
                )
                
                session.add(gasto)
                
                # Actualizar caja
                caja.gastos_dia = (caja.gastos_dia or 0) + monto_float
                
                session.commit()
                
                logger.info(f"Gasto registrado: ${monto_float} - {descripcion}")
                
                return {
                    "success": True,
                    "mensaje": "Gasto registrado exitosamente",
                    "monto": monto_float,
                    "descripcion": descripcion,
                    "categoria": categoria,
                    "gasto_id": gasto.id[:8]
                }
                
        except ValueError:
            return {"success": False, "error": "Monto inválido"}
        except Exception as e:
            logger.error(f"Error registrando gasto: {e}")
            return {"success": False, "error": f"Error del sistema: {str(e)}"}

# ==================== API DE PRODUCTOS ====================

class ProductosAPI:
    """API para gestión de productos."""
    
    @staticmethod
    def obtener_productos(
        filtro: str = "",
        solo_bajo_stock: bool = False,
        categoria: str = ""
    ) -> List[Dict[str, Any]]:
        """Obtiene la lista de productos."""
        if not MODELS_AVAILABLE:
            # Datos de ejemplo para desarrollo
            return [
                {
                    "id": "1",
                    "nombre": "Vacio",
                    "precio": 12.99,
                    "stock": 50.0,
                    "unidad": "kg",
                    "categoria": "CORTES",
                    "tipo": "ROTACION"
                },
                {
                    "id": "2", 
                    "nombre": "Bife de Chorizo",
                    "precio": 15.50,
                    "stock": 30.0,
                    "unidad": "kg",
                    "categoria": "CORTES",
                    "tipo": "PREMIUM"
                },
                {
                    "id": "3",
                    "nombre": "Nalga",
                    "precio": 7.00,
                    "stock": 40.0,
                    "unidad": "kg",
                    "categoria": "CORTES",
                    "tipo": "ROTACION"
                }
            ]
        
        try:
            with db_manager.get_session() as session:
                query = session.query(ProductoElaborado)
                
                # Aplicar filtros
                if filtro:
                    query = query.filter(ProductoElaborado.nombre.ilike(f"%{filtro}%"))
                
                if solo_bajo_stock:
                    query = query.filter(ProductoElaborado.stock_actual < 5)
                
                if categoria:
                    query = query.filter(ProductoElaborado.tipo == categoria)
                
                productos = query.order_by(ProductoElaborado.nombre).all()
                
                resultado = []
                for p in productos:
                    # Determinar nivel de stock
                    nivel_stock = "NORMAL"
                    if p.stock_actual is None or p.stock_actual <= 0:
                        nivel_stock = "AGOTADO"
                    elif p.stock_actual < 5:
                        nivel_stock = "BAJO"
                    
                    resultado.append({
                        "id": p.id,
                        "nombre": p.nombre,
                        "precio": float(p.precio_venta or 0),
                        "stock": float(p.stock_actual or 0),
                        "unidad": "kg",
                        "categoria": p.tipo or "CARNES",
                        "tipo": p.tipo or "ROTACION",
                        "nivel_stock": nivel_stock
                    })
                
                return resultado
                
        except Exception as e:
            logger.error(f"Error obteniendo productos: {e}")
            return []
    
    @staticmethod
    def obtener_producto_por_id(producto_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por su ID."""
        if not MODELS_AVAILABLE:
            return None
        
        try:
            with db_manager.get_session() as session:
                producto = session.query(ProductoElaborado).get(producto_id)
                
                if not producto:
                    return None
                
                return {
                    "id": producto.id,
                    "nombre": producto.nombre,
                    "precio": float(producto.precio_venta or 0),
                    "stock": float(producto.stock_actual or 0),
                    "unidad": "kg",
                    "categoria": producto.tipo or "CARNES"
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo producto: {e}")
            return None

# ==================== API DE MOVIMIENTOS ====================

class MovimientosAPI:
    """API para gestión de movimientos."""
    
    @staticmethod
    def obtener_movimientos_dia(
        limite: int = 50,
        tipo: str = None
    ) -> Dict[str, Any]:
        """Obtiene los movimientos del día actual."""
        if not MODELS_AVAILABLE:
            return {
                "movimientos": [],
                "total": 0,
                "resumen": {
                    "total_ventas": 0,
                    "total_gastos": 0,
                    "balance": 0
                }
            }
        
        try:
            with db_manager.get_session() as session:
                hoy = date.today()
                movimientos = []
                
                # Obtener ventas del día
                query_ventas = session.query(Venta).filter_by(fecha=hoy)
                if tipo and tipo != 'GASTO':
                    query_ventas = query_ventas.filter_by(tipo_pago=tipo)
                
                ventas = query_ventas.order_by(Venta.hora.desc()).limit(limite).all()
                
                for venta in ventas:
                    movimientos.append({
                        "id": venta.id[:8],
                        "tipo": "VENTA",
                        "tipo_pago": venta.tipo_pago,
                        "monto": float(venta.total or 0),
                        "hora": venta.hora.strftime('%H:%M:%S') if venta.hora else 'N/A',
                        "fecha": venta.fecha.strftime('%Y-%m-%d') if venta.fecha else 'N/A',
                        "detalles": f"Venta #{venta.id[:8]}",
                        "cliente": venta.cliente.nombre if venta.cliente else "Cliente general",
                        "icono": "fa-cart-plus",
                        "color": "success"
                    })
                
                # Obtener gastos del día
                if not tipo or tipo == 'GASTO':
                    gastos = session.query(Gasto).filter_by(fecha=hoy).order_by(Gasto.fecha.desc()).limit(limite).all()
                    
                    for gasto in gastos:
                        movimientos.append({
                            "id": gasto.id[:8],
                            "tipo": "GASTO",
                            "tipo_pago": "",
                            "monto": -float(gasto.monto or 0),
                            "hora": "N/A",
                            "fecha": gasto.fecha.strftime('%Y-%m-%d') if gasto.fecha else 'N/A',
                            "detalles": gasto.descripcion,
                            "categoria": gasto.categoria,
                            "icono": "fa-money-bill-wave",
                            "color": "warning"
                        })
                
                # Ordenar por fecha/hora (más recientes primero)
                movimientos.sort(key=lambda x: (
                    x.get('fecha', ''),
                    x.get('hora', '')
                ), reverse=True)
                
                # Calcular resumen
                total_ventas = sum(m['monto'] for m in movimientos if m['tipo'] == 'VENTA')
                total_gastos = abs(sum(m['monto'] for m in movimientos if m['tipo'] == 'GASTO'))
                balance = total_ventas - total_gastos
                
                return {
                    "movimientos": movimientos[:limite],
                    "total": len(movimientos),
                    "resumen": {
                        "total_ventas": float(total_ventas),
                        "total_gastos": float(total_gastos),
                        "balance": float(balance)
                    }
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo movimientos: {e}")
            return {
                "movimientos": [],
                "total": 0,
                "resumen": {
                    "total_ventas": 0,
                    "total_gastos": 0,
                    "balance": 0
                }
            }

# ==================== API DE REPORTES ====================

class ReportesAPI:
    """API para generación de reportes."""
    
    @staticmethod
    def generar_reporte_ventas(
        fecha_inicio: str = None,
        fecha_fin: str = None
    ) -> Dict[str, Any]:
        """Genera reporte de ventas."""
        try:
            # Parsear fechas
            if fecha_inicio:
                fecha_ini = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            else:
                fecha_ini = date.today() - timedelta(days=30)
            
            if fecha_fin:
                fecha_fin_date = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            else:
                fecha_fin_date = date.today()
            
            if not MODELS_AVAILABLE:
                # Datos simulados para desarrollo
                return {
                    "periodo": {
                        "inicio": fecha_ini.strftime('%Y-%m-%d'),
                        "fin": fecha_fin_date.strftime('%Y-%m-%d'),
                        "dias": (fecha_fin_date - fecha_ini).days
                    },
                    "resumen": {
                        "total_ventas": 125000.50,
                        "cantidad_ventas": 342,
                        "promedio_diario": 4166.68,
                        "promedio_ticket": 365.50
                    },
                    "por_tipo_pago": {
                        "EFECTIVO": 87500.35,
                        "TARJETA": 37500.15
                    },
                    "productos_mas_vendidos": [
                        {"producto": "Carne Molida", "cantidad": 120.5, "total": 1807.50},
                        {"producto": "Vacio", "cantidad": 85.3, "total": 1108.90},
                        {"producto": "Asado", "cantidad": 67.8, "total": 745.80}
                    ],
                    "ventas_por_dia": [
                        {"fecha": "2024-01-01", "total": 4200.00, "cantidad": 12},
                        {"fecha": "2024-01-02", "total": 3800.00, "cantidad": 10}
                    ]
                }
            
            with db_manager.get_session() as session:
                # Obtener ventas del período
                ventas = session.query(Venta).filter(
                    Venta.fecha >= fecha_ini,
                    Venta.fecha <= fecha_fin_date
                ).all()
                
                # Calcular resumen
                total_ventas = sum(v.total for v in ventas)
                cantidad_ventas = len(ventas)
                dias_periodo = max((fecha_fin_date - fecha_ini).days, 1)
                
                # Por tipo de pago
                por_tipo_pago = {}
                for venta in ventas:
                    tipo = venta.tipo_pago
                    if tipo not in por_tipo_pago:
                        por_tipo_pago[tipo] = 0.0
                    por_tipo_pago[tipo] += float(venta.total or 0)
                
                # Ventas por día
                ventas_por_dia = []
                fecha_actual = fecha_ini
                while fecha_actual <= fecha_fin_date:
                    ventas_dia = [v for v in ventas if v.fecha == fecha_actual]
                    total_dia = sum(v.total for v in ventas_dia)
                    ventas_por_dia.append({
                        "fecha": fecha_actual.strftime('%Y-%m-%d'),
                        "total": float(total_dia),
                        "cantidad": len(ventas_dia)
                    })
                    fecha_actual += timedelta(days=1)
                
                return {
                    "periodo": {
                        "inicio": fecha_ini.strftime('%Y-%m-%d'),
                        "fin": fecha_fin_date.strftime('%Y-%m-%d'),
                        "dias": dias_periodo
                    },
                    "resumen": {
                        "total_ventas": float(total_ventas),
                        "cantidad_ventas": cantidad_ventas,
                        "promedio_diario": float(total_ventas) / dias_periodo,
                        "promedio_ticket": float(total_ventas) / cantidad_ventas if cantidad_ventas > 0 else 0
                    },
                    "por_tipo_pago": por_tipo_pago,
                    "ventas_por_dia": ventas_por_dia
                }
                
        except Exception as e:
            logger.error(f"Error generando reporte de ventas: {e}")
            return {
                "error": f"Error generando reporte: {str(e)}",
                "periodo": {
                    "inicio": fecha_inicio or date.today().strftime('%Y-%m-%d'),
                    "fin": fecha_fin or date.today().strftime('%Y-%m-%d'),
                    "dias": 0
                },
                "resumen": {
                    "total_ventas": 0,
                    "cantidad_ventas": 0,
                    "promedio_diario": 0,
                    "promedio_ticket": 0
                }
            }
    
    @staticmethod
    def generar_reporte_inventario() -> Dict[str, Any]:
        """Genera reporte de inventario."""
        if not MODELS_AVAILABLE:
            # Datos simulados
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
                    {"nombre": "Morcilla", "stock": 3.0, "umbral": 10.0}
                ]
            }
        
        try:
            with db_manager.get_session() as session:
                # Obtener todos los productos
                productos = session.query(ProductoElaborado).all()
                
                total_productos = len(productos)
                valor_total = 0.0
                productos_bajo_stock = 0
                productos_agotados = 0
                productos_por_categoria = {}
                productos_criticos = []
                
                for p in productos:
                    stock = p.stock_actual or 0
                    
                    # Calcular valor (usando precio de venta como referencia)
                    valor_producto = stock * (p.precio_venta or 0)
                    valor_total += valor_producto
                    
                    # Contar por categoría
                    categoria = p.tipo or "OTROS"
                    if categoria not in productos_por_categoria:
                        productos_por_categoria[categoria] = 0
                    productos_por_categoria[categoria] += 1
                    
                    # Verificar stock crítico
                    if stock <= 0:
                        productos_agotados += 1
                        productos_criticos.append({
                            "nombre": p.nombre,
                            "stock": float(stock),
                            "umbral": 0,
                            "estado": "AGOTADO"
                        })
                    elif stock < 5:  # Umbral fijo por ahora
                        productos_bajo_stock += 1
                        productos_criticos.append({
                            "nombre": p.nombre,
                            "stock": float(stock),
                            "umbral": 5.0,
                            "estado": "BAJO"
                        })
                
                return {
                    "total_productos": total_productos,
                    "valor_total_inventario": float(valor_total),
                    "productos_bajo_stock": productos_bajo_stock,
                    "productos_agotados": productos_agotados,
                    "productos_por_categoria": productos_por_categoria,
                    "productos_criticos": productos_criticos[:10]  # Solo los 10 más críticos
                }
                
        except Exception as e:
            logger.error(f"Error generando reporte de inventario: {e}")
            return {
                "total_productos": 0,
                "valor_total_inventario": 0,
                "productos_bajo_stock": 0,
                "productos_agotados": 0,
                "productos_por_categoria": {},
                "productos_criticos": []
            }

# ==================== FACHADA PRINCIPAL ====================

class BackendAPI:
    """Fachada principal para el backend."""
    
    def __init__(self):
        self.caja = CajaAPI()
        self.productos = ProductosAPI()
        self.movimientos = MovimientosAPI()
        self.reportes = ReportesAPI()  # CORREGIDO: ReportesAPI SÍ existe
    
    # Métodos de conveniencia
    def obtener_estado_caja(self):
        return self.caja.obtener_estado_caja()
    
    def abrir_caja(self, monto_inicial, responsable):
        return self.caja.abrir_caja(monto_inicial, responsable)
    
    def cerrar_caja(self, efectivo_real):
        return self.caja.cerrar_caja(efectivo_real)
    
    def registrar_venta(self, tipo_pago, monto, detalles="", cliente_nombre=""):
        return self.caja.registrar_venta(tipo_pago, monto, detalles, cliente_nombre)
    
    def registrar_gasto(self, descripcion, monto, categoria="GASTO"):
        return self.caja.registrar_gasto(descripcion, monto, categoria)
    
    def obtener_movimientos(self, limite=50, tipo=None):
        return self.movimientos.obtener_movimientos_dia(limite, tipo)
    
    def obtener_productos(self, filtro="", solo_bajo_stock=False, categoria=""):
        return self.productos.obtener_productos(filtro, solo_bajo_stock, categoria)
    
    def obtener_producto_por_id(self, producto_id):
        return self.productos.obtener_producto_por_id(producto_id)
    
    def generar_reporte_ventas(self, fecha_inicio=None, fecha_fin=None):
        return self.reportes.generar_reporte_ventas(fecha_inicio, fecha_fin)
    
    def generar_reporte_inventario(self):
        return self.reportes.generar_reporte_inventario()
    
    def sistema_listo(self):
        """Verifica si el sistema está listo para operar."""
        return {
            "sqlalchemy": SQLALCHEMY_AVAILABLE,
            "modelos": MODELS_AVAILABLE,
            "db_manager": hasattr(db_manager, 'get_session') if 'db_manager' in globals() else False,
            "timestamp": datetime.now().isoformat(),
            "estado": "OK" if MODELS_AVAILABLE else "ERROR"
        }

# ==================== INSTANCIA GLOBAL ====================

# Crear instancia global
backend_instance = BackendAPI()

# Exportar funciones de conveniencia
obtener_estado_caja = backend_instance.obtener_estado_caja
abrir_caja = backend_instance.abrir_caja
cerrar_caja = backend_instance.cerrar_caja
registrar_venta = backend_instance.registrar_venta
obtener_movimientos = backend_instance.obtener_movimientos
obtener_productos = backend_instance.obtener_productos
sistema_listo = backend_instance.sistema_listo

# Exportar la instancia principal
backend = backend_instance

# ==================== PRUEBAS ====================

if __name__ == "__main__":
    print("🧪 Probando Backend API...")
    print(f"📦 SQLAlchemy disponible: {SQLALCHEMY_AVAILABLE}")
    print(f"📦 Modelos disponibles: {MODELS_AVAILABLE}")
    
    # Probar estado del sistema
    estado_sistema = backend.sistema_listo()
    print(f"📊 Estado del sistema: {estado_sistema}")
    