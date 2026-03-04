# app/modelos.py - VERSIÓN COMPLETA Y CORREGIDA
from datetime import datetime, date
import uuid
from sqlalchemy import (
    Column, String, Float, Integer, ForeignKey,
    Date, DateTime, Boolean, Text
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

# ============================================================
#                      MODELOS PRINCIPALES
# ============================================================

# ------------------------------------------------------------
#                       CLIENTE
# ------------------------------------------------------------
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(String, primary_key=True, default=generate_uuid)
    nombre = Column(String, nullable=False)
    telefono = Column(String)
    direccion = Column(String)
    tipo = Column(String, default="MINORISTA")  # MINORISTA, MAYORISTA
    limite_credito = Column(Float, default=0.0)
    saldo_pendiente = Column(Float, default=0.0)

    # Relación con ventas
    ventas = relationship("Venta", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente {self.nombre}>"

# ------------------------------------------------------------
#                       EMPLEADO
# ------------------------------------------------------------
class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(String, primary_key=True, default=generate_uuid)
    nombre = Column(String, nullable=False)
    legajo = Column(String)
    comision_pct = Column(Float, default=0.0)

    ventas = relationship("Venta", back_populates="empleado")

    def __repr__(self):
        return f"<Empleado {self.nombre}>"

# ------------------------------------------------------------
#                     MATERIA PRIMA
# ------------------------------------------------------------
class MateriaPrima(Base):
    __tablename__ = "materias_primas"

    id = Column(String, primary_key=True, default=generate_uuid)
    nombre = Column(String, nullable=False)
    unidad = Column(String, default="kg")
    costo_referencia = Column(Float, default=0.0)

    def __repr__(self):
        return f"<MateriaPrima {self.nombre}>"

# ------------------------------------------------------------
#                       PROVEEDOR
# ------------------------------------------------------------
class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(String, primary_key=True, default=generate_uuid)
    razon_social = Column(String, nullable=False)
    cuit = Column(String, unique=True)
    dias_pago = Column(Integer, default=30)

    def __repr__(self):
        return f"<Proveedor {self.razon_social}>"

# ------------------------------------------------------------
#                           LOTE
# ------------------------------------------------------------
class Lote(Base):
    __tablename__ = "lotes"

    id = Column(String, primary_key=True, default=generate_uuid)
    num_tropa = Column(String, unique=True)
    
    materia_prima_id = Column(String, ForeignKey("materias_primas.id"))
    materia_prima = relationship("MateriaPrima")
    
    proveedor_id = Column(String, ForeignKey("proveedores.id"))
    proveedor = relationship("Proveedor")
    
    fecha_faena = Column(Date)
    peso_inicial = Column(Float, default=0.0)
    peso_restante = Column(Float, default=0.0)
    costo_total = Column(Float, default=0.0)
    
    @property
    def costo_real_kg(self):
        if self.peso_inicial and self.peso_inicial > 0:
            return round(self.costo_total / self.peso_inicial, 2)
        return 0.0

    def __repr__(self):
        return f"<Lote {self.num_tropa} - {self.peso_restante:.2f} kg restante>"

# ------------------------------------------------------------
#                     PRODUCTO ELABORADO
# ------------------------------------------------------------
class ProductoElaborado(Base):
    __tablename__ = "productos_elaborados"

    id = Column(String, primary_key=True, default=generate_uuid)
    nombre = Column(String, nullable=False)
    stock_actual = Column(Float, default=0.0)
    precio_venta = Column(Float, nullable=False)
    tipo = Column(String, default="ROTACION")  # ROTACION, PREMIUM, BAJO_VALOR
    costo_ultima_compra = Column(Float, default=0.0)

    # Relación con items de venta
    items = relationship("VentaItem", back_populates="producto")

    def verificar_stock(self, cantidad):
        return self.stock_actual >= cantidad

    def reducir_stock(self, cantidad):
        self.stock_actual -= cantidad

    def aumentar_stock(self, cantidad):
        self.stock_actual += cantidad

    def __repr__(self):
        return f"<ProductoElaborado {self.nombre}>"

# ------------------------------------------------------------
#                           CAJA
# ------------------------------------------------------------
class Caja(Base):
    __tablename__ = "cajas"

    id = Column(String, primary_key=True, default=generate_uuid)
    fecha = Column(Date, default=date.today)
    estado = Column(String, default="cerrada")   # abierta / cerrada
    responsable = Column(String)
    hora_apertura = Column(DateTime)
    hora_cierre = Column(DateTime)

    monto_inicial = Column(Float, default=0.0)
    ventas_efectivo = Column(Float, default=0.0)
    ventas_tarjeta = Column(Float, default=0.0)
    gastos_dia = Column(Float, default=0.0)
    efectivo_real = Column(Float)

    # Relación con las ventas del día
    ventas = relationship("Venta", back_populates="caja")

    def efectivo_esperado(self):
        return round(
            (self.monto_inicial or 0)
            + (self.ventas_efectivo or 0)
            - (self.gastos_dia or 0),
            2
        )

    def __repr__(self):
        return f"<Caja {self.fecha} - {self.estado}>"

# ------------------------------------------------------------
#                            VENTA
# ------------------------------------------------------------
class Venta(Base):
    __tablename__ = "ventas"

    id = Column(String, primary_key=True, default=generate_uuid)
    fecha = Column(Date, default=date.today)
    hora = Column(DateTime, default=datetime.now)

    tipo_pago = Column(String, nullable=False)   # EFECTIVO / TARJETA / TRANSFERENCIA / CREDITO
    total = Column(Float, default=0.0)

    # Relaciones
    cliente_id = Column(String, ForeignKey("clientes.id"), nullable=True)
    cliente = relationship("Cliente", back_populates="ventas")

    empleado_id = Column(String, ForeignKey("empleados.id"), nullable=True)
    empleado = relationship("Empleado", back_populates="ventas")

    caja_id = Column(String, ForeignKey("cajas.id"), nullable=True)
    caja = relationship("Caja", back_populates="ventas")

    # Ítems de la venta
    items = relationship(
        "VentaItem",
        back_populates="venta",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Venta {self.id} - {self.total}>"

# ------------------------------------------------------------
#                          VENTA ITEM
# ------------------------------------------------------------
class VentaItem(Base):
    __tablename__ = "venta_items"

    id = Column(String, primary_key=True, default=generate_uuid)

    venta_id = Column(String, ForeignKey("ventas.id"), nullable=False)
    venta = relationship("Venta", back_populates="items")

    producto_id = Column(String, ForeignKey("productos_elaborados.id"), nullable=False)
    producto = relationship("ProductoElaborado", back_populates="items")

    cantidad_kg = Column(Float, nullable=False)
    precio_vendido = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    def __repr__(self):
        return f"<Item {self.producto.nombre} x {self.cantidad_kg}>"

# ------------------------------------------------------------
#                            GASTO
# ------------------------------------------------------------
class Gasto(Base):
    __tablename__ = "gastos"

    id = Column(String, primary_key=True, default=generate_uuid)
    caja_id = Column(String, ForeignKey("cajas.id"))

    descripcion = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    categoria = Column(String, default="GASTO")
    fecha = Column(Date, default=date.today)

    def __repr__(self):
        return f"<Gasto {self.descripcion} - {self.monto}>"

# ------------------------------------------------------------
#                     CUENTA POR COBRAR
# ------------------------------------------------------------
class CuentaPorCobrar(Base):
    __tablename__ = "cuentas_por_cobrar"

    id = Column(String, primary_key=True, default=generate_uuid)
    cliente_id = Column(String, ForeignKey("clientes.id"))
    cliente = relationship("Cliente")
    
    venta_id = Column(String, ForeignKey("ventas.id"))
    venta = relationship("Venta")
    
    monto = Column(Float, default=0.0)
    fecha_emision = Column(Date, default=date.today)
    fecha_vencimiento = Column(Date)
    estado = Column(String, default="PENDIENTE")  # PENDIENTE, PAGADA, VENCIDA
    
    def __repr__(self):
        return f"<CuentaPorCobrar {self.cliente.nombre} - ${self.monto:.2f}>"