import unittest
from datetime import date

# Importamos SOLO lógica de negocio
from app.procesos import (
    ProcesoDeDespiece,
    Venta,
    AlertaStockManager,
    CreditoManager,
)

# =========================================================
# ENTIDADES SIMPLES DE DOMINIO (DOBLES DE TEST)
# =========================================================

class Producto:
    def __init__(self, nombre, precio, stock=0.0):
        self.nombre = nombre
        self.precio_venta = precio
        self.stock_actual = stock
        self.costo_ultima_compra = 0.0

    def verificar_stock(self, cantidad):
        return self.stock_actual >= cantidad

    def reducir_stock(self, cantidad):
        self.stock_actual -= cantidad

    def aumentar_stock(self, cantidad):
        self.stock_actual += cantidad


class Cliente:
    def __init__(self, nombre, limite_credito=0.0):
        self.nombre = nombre
        self.limite_credito = limite_credito
        self.saldo_pendiente = 0.0


class Empleado:
    def __init__(self, nombre):
        self.nombre = nombre


class Lote:
    def __init__(self, peso_inicial, costo_total):
        self.peso_inicial = peso_inicial
        self.peso_restante = peso_inicial
        self.costo_total = costo_total

    @property
    def costo_real_kg(self):
        return round(self.costo_total / self.peso_inicial, 2)


# =========================================================
# TESTS DE PROCESOS (DOMINIO PURO)
# =========================================================

class TestProcesos(unittest.TestCase):

    def setUp(self):
        # Productos
        self.solomillo = Producto("Solomillo", precio=25.0)
        self.merma = Producto("Merma", precio=0.0)

        # Cliente y empleado
        self.cliente = Cliente("Supermercado XYZ", limite_credito=1000.0)
        self.empleado = Empleado("Ana")

        # Lote
        self.lote = Lote(peso_inicial=100.0, costo_total=400.0)

    # -----------------------------------------------------
    # PROCESO DE DESPIECE
    # -----------------------------------------------------

    def test_proceso_despiece_actualiza_stock_y_lote(self):
        proceso = ProcesoDeDespiece(self.lote, peso_procesado=10.0)

        rendimiento = {
            self.solomillo: 8.0
        }

        proceso.ejecutar_proceso(rendimiento, self.merma)

        # Lote
        self.assertEqual(self.lote.peso_restante, 90.0)

        # Producto
        self.assertEqual(self.solomillo.stock_actual, 8.0)
        self.assertEqual(self.solomillo.costo_ultima_compra, 4.0)

    # -----------------------------------------------------
    # VENTA A CRÉDITO
    # -----------------------------------------------------

    def test_venta_credito_actualiza_stock_y_saldo(self):
        self.solomillo.stock_actual = 50.0

        venta = Venta(
            cliente=self.cliente,
            empleado=self.empleado,
            tipo_pago="CREDITO"
        )

        venta.agregar_item(self.solomillo, cantidad=10.0, precio=25.0)
        venta.cerrar_venta()

        self.assertEqual(self.solomillo.stock_actual, 40.0)
        self.assertEqual(self.cliente.saldo_pendiente, 250.0)
        self.assertEqual(venta.total, 250.0)

    # -----------------------------------------------------
    # ALERTA DE MARGEN
    # -----------------------------------------------------

    def test_alerta_margen_bajo(self):
        self.solomillo.stock_actual = 10.0
        self.solomillo.costo_ultima_compra = 10.0
        self.solomillo.precio_venta = 12.0  # margen bajo

        manager = AlertaStockManager([self.solomillo])

        alertas = manager.generar_alertas()

        self.assertEqual(len(alertas), 1)

    # -----------------------------------------------------
    # ALERTA DE CRÉDITO
    # -----------------------------------------------------

    def test_alerta_limite_credito(self):
        self.cliente.saldo_pendiente = 950.0  # > 90% de 1000

        manager = CreditoManager([], [self.cliente])

        alertas = manager.verificar_limite_global()

        self.assertEqual(len(alertas), 1)


if __name__ == "__main__":
    unittest.main()
