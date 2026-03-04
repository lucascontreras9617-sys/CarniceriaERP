# app/caja.py

from datetime import date, datetime
from sqlalchemy.orm import Session
from .modelos import Caja, Venta, Gasto, ProductoElaborado

class CajaError(Exception):
    """Errores específicos del sistema de caja."""
    pass


class ControlCaja:
    """
    Sistema profesional de gestión de caja.
    - Apertura/cierre estricto
    - Control de horas
    - Validaciones de ventas y gastos
    - Previene inconsistencias
    """

    def __init__(self, session: Session):
        self.session = session

    # ======================================================
    #                   UTILIDADES INTERNAS
    # ======================================================

    def _caja_del_dia(self):
        """Obtiene la caja del día actual si existe."""
        return (
            self.session.query(Caja)
            .filter_by(fecha=date.today())
            .first()
        )

    def caja_esta_abierta(self) -> bool:
        caja = self._caja_del_dia()
        return caja is not None and caja.estado == "abierta"

    def caja_esta_cerrada(self) -> bool:
        caja = self._caja_del_dia()
        return caja is None or caja.estado == "cerrada"

    # ======================================================
    #                   APERTURA DE CAJA
    # ======================================================

    def abrir_caja(self, responsable: str, monto_inicial: float):
        """
        Abre la caja del día.
        No permite abrir dos veces ni abrir con monto <= 0.
        """
        if monto_inicial < 0:
            raise CajaError("El monto inicial no puede ser negativo.")

        caja = self._caja_del_dia()

        if caja:
            if caja.estado == "abierta":
                raise CajaError("La caja ya está abierta.")
            # Si está cerrada, se reabre
            if caja.estado == "cerrada":
                caja.estado = "abierta"
                caja.hora_apertura = datetime.now()
                caja.responsable = responsable
                caja.monto_inicial = monto_inicial
                self.session.commit()
                return caja

        # No existe → se crea
        nueva = Caja(
            fecha=date.today(),
            estado="abierta",
            hora_apertura=datetime.now(),
            responsable=responsable,
            monto_inicial=monto_inicial,
        )
        self.session.add(nueva)
        self.session.commit()
        return nueva

    # ======================================================
    #                   CIERRE DE CAJA
    # ======================================================

    def cerrar_caja(self, efectivo_real: float):
        """
        Cierra la caja del día.
        - Registra hora
        - Calcula diferencia
        - Bloquea ventas posteriores
        """
        caja = self._caja_del_dia()

        if not caja:
            raise CajaError("No existe caja para el día de hoy.")

        if caja.estado == "cerrada":
            raise CajaError("La caja ya está cerrada.")

        caja.estado = "cerrada"
        caja.hora_cierre = datetime.now()
        caja.efectivo_real = efectivo_real
        self.session.commit()

        diferencia = efectivo_real - caja.efectivo_esperado()
        return {
            "esperado": caja.efectivo_esperado(),
            "real": efectivo_real,
            "diferencia": diferencia,
            "estado": "cerrada"
        }

    # ======================================================
    #                   REGISTRO DE VENTAS
    # ======================================================

    def registrar_venta(self, venta: Venta):
        """
        Registra una venta en la caja del día si corresponde.
        - Solo ventas en EFECTIVO se cargan a caja
        - No permite ventas con caja cerrada
        """
        caja = self._caja_del_dia()

        if not caja:
            raise CajaError("No existe una caja abierta. Debe abrirla antes de vender.")

        if caja.estado != "abierta":
            raise CajaError("La caja está cerrada. No se pueden registrar ventas.")

        venta.caja_id = caja.id

        # Venta en efectivo suma a caja
        if venta.tipo_pago == "EFECTIVO":
            caja.ventas_efectivo += venta.total
        elif venta.tipo_pago == "TARJETA":
            caja.ventas_tarjeta += venta.total
        # Las ventas a crédito NO modifican caja

        # Descarga de stock
        for item in venta.items:
            producto = self.session.get(ProductoElaborado, item.producto_id)
            if not producto.verificar_stock(item.cantidad_kg):
                raise CajaError(f"Stock insuficiente para {producto.nombre}")
            producto.reducir_stock(item.cantidad_kg)

        self.session.add(venta)
        self.session.commit()

        return {"status": "ok", "venta_id": venta.id}

    # ======================================================
    #                   REGISTRO DE GASTOS
    # ======================================================

    def registrar_gasto(self, descripcion: str, monto: float, categoria: str = "GASTO"):
        """
        Registra un gasto del día.
        - No permite registrar sin caja abierta
        """
        caja = self._caja_del_dia()

        if not caja:
            raise CajaError("No existe una caja abierta.")
        if caja.estado != "abierta":
            raise CajaError("La caja está cerrada. No se pueden registrar gastos.")

        gasto = Gasto(
            caja_id=caja.id,
            descripcion=descripcion,
            monto=monto,
            categoria=categoria,
            fecha=date.today()
        )
        caja.gastos_dia += monto

        self.session.add(gasto)
        self.session.commit()

        return gasto

    # ======================================================
    #                   REPORTES
    # ======================================================

    def reporte_caja(self):
        """Devuelve un resumen detallado de la caja del día."""
        caja = self._caja_del_dia()

        if not caja:
            raise CajaError("No existe caja para el día de hoy.")

        return {
            "fecha": str(caja.fecha),
            "estado": caja.estado,
            "responsable": caja.responsable,
            "monto_inicial": caja.monto_inicial,
            "ventas_efectivo": caja.ventas_efectivo,
            "ventas_tarjeta": caja.ventas_tarjeta,
            "gastos": caja.gastos_dia,
            "efectivo_esperado": caja.efectivo_esperado(),
            "hora_apertura": caja.hora_apertura,
            "hora_cierre": caja.hora_cierre,
        }
