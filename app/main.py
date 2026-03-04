# app/main.py (VERSIÓN ULTRA-PROFESIONAL)
import sys
import os
from datetime import datetime, timedelta, date
from app.infraestructura.persistence.orm.modelos import ProductoElaborado, Lote, Proveedor, MateriaPrima, Cliente, Empleado
from app.procesos import ProcesoDeDespiece, Venta, CuentaPorCobrar, ReporteManager, AlertaStockManager, CreditoManager
from app.persistencia import db_manager

# --- 0. Configurar rutas ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

print(f"📁 Directorio actual: {current_dir}")
print(f"📁 Raíz del proyecto: {project_root}")

# --- 1. Helper genérico get_or_create ---
def get_or_create(modelo, atributo, valor, **kwargs):
    with db_manager.get_session() as session:
        obj = session.query(modelo).filter(getattr(modelo, atributo) == valor).first()
        if not obj:
            obj = modelo(**kwargs)
            session.add(obj)
            session.commit()
    return obj

# --- 2. Inicialización de Datos ---
def inicializar_productos():
    productos = [
        ("Vacio", 12.99, "ROTACION"),
        ("Bife de Chorizo", 15.50, "PREMIUM"),
        ("Nalga", 7.00, "ROTACION"),
        ("Primo Molido", 7.50, "ROTACION"),
        ("Grasa y Hueso (Merma)", 0.50, "BAJO_VALOR")
    ]
    return {nombre: get_or_create(ProductoElaborado, "nombre", nombre, nombre=nombre, precio_venta=precio, tipo=tipo)
            for nombre, precio, tipo in productos}

def inicializar_materia_prima():
    return get_or_create(MateriaPrima, "nombre", "Res de Vaca", nombre="Res de Vaca", unidad="kg", costo_referencia=0.0)

def inicializar_proveedor():
    return get_or_create(Proveedor, "cuit", "30-12345678-9", razon_social="Frigorífico Don Pepe S.A.", cuit="30-12345678-9", dias_pago=30)

def inicializar_clientes_empleados():
    empleados = {
        "Carlos": get_or_create(Empleado, "legajo", "C01", nombre="Carlos", legajo="C01", comision_pct=0.015)
    }
    clientes = {
        "Juan Pérez": get_or_create(Cliente, "nombre", "Juan Pérez", nombre="Juan Pérez", tipo="MINORISTA"),
        "El Bife de Oro": get_or_create(Cliente, "nombre", "El Bife de Oro", nombre="El Bife de Oro", tipo="MAYORISTA", limite_credito=500.0)
    }
    return empleados, clientes

def inicializar_lote(materia_prima, proveedor):
    with db_manager.get_session() as session:
        lote = session.query(Lote).filter(Lote.num_tropa == "T-4589").first()
        if not lote:
            lote = Lote(
                num_tropa="T-4589",
                materia_prima=materia_prima,
                proveedor=proveedor,
                fecha_faena=date(2025, 12, 5),
                peso_inicial=100.0,
                peso_restante=100.0,
                costo_total=550.0
            )
            session.add(lote)
            session.commit()
        
        # FORZAR CARGA de relaciones ANTES de cerrar la sesión
        session.refresh(lote)  # Refrescar desde DB
        # Cargar explícitamente las relaciones
        _ = lote.materia_prima  # Esto carga la relación
        _ = lote.proveedor      # Esto carga la relación
        session.expunge(lote)   # Desconectar de sesión pero con datos cargados
        
    return lote

# --- 3. Simulación de Despiece ---
def simular_despiece(lote, productos):
    print("\n=== INVENTARIO ANTES DEL PROCESO ===")
    print(lote, productos["Vacio"], productos["Grasa y Hueso (Merma)"], sep="\n")
    print("-" * 30)

    despiece = ProcesoDeDespiece(lote=lote, cantidad_a_procesar=50.0)
    rendimiento = {
        productos["Vacio"]: 5.0,
        productos["Bife de Chorizo"]: 8.0,
        productos["Nalga"]: 12.0,
        productos["Primo Molido"]: 20.0
    }
    despiece.ejecutar_proceso(rendimiento=rendimiento, producto_merma=productos["Grasa y Hueso (Merma)"])

    print("\n=== INVENTARIO DESPUÉS DEL PROCESO ===")
    print(lote)
    print(f"Costo real del Lote: ${lote.costo_real_kg:.2f}/kg")
    for p in productos.values():
        print(p)
    return despiece

# --- 4. Simulación de Venta ---
def simular_venta(clientes, empleados, productos):
    venta = Venta(cliente=clientes["El Bife de Oro"], empleado=empleados["Carlos"], tipo_pago='CREDITO')
    venta.agregar_item(productos["Bife de Chorizo"], 5.0, 16.00)
    venta.agregar_item(productos["Nalga"], 10.0, 10.50)
    venta.cerrar_venta()

    cc = CuentaPorCobrar(
        id_venta=venta.id,
        cliente=clientes["El Bife de Oro"],
        monto=venta.total,
        dias_credito=30
    )
    cc.fecha_emision = datetime.now() - timedelta(days=35)
    return venta, cc

# --- 5. Reportes y Alertas ---
def generar_reportes_alertas(lista_ventas, lista_lotes, lista_productos, lista_cuentas_cobrar, lista_clientes):
    reporte_mgr = ReporteManager(lista_ventas, lista_lotes, lista_productos)
    lista_productos[2].precio_venta = 7.0  # Forzar alerta sobre nalga
    reporte_mgr.reporte_margen_por_corte()
    reporte_mgr.reporte_rendimiento_lote(lista_lotes[0])

    alerta_mgr = AlertaStockManager(lista_productos)
    alertas = alerta_mgr.generar_alertas()

    credito_mgr = CreditoManager(lista_cuentas_cobrar, lista_clientes)
    credito_mgr.generar_reporte_vencidas()
    credito_mgr.verificar_limite_global()
    return alertas

# --- 6. Ejecución Principal ---
if __name__ == "__main__":
    print("🔧 Inicializando ERP Carnicería...")

    productos = inicializar_productos()
    materia_prima = inicializar_materia_prima()
    proveedor = inicializar_proveedor()
    lote = inicializar_lote(materia_prima, proveedor)
    empleados, clientes = inicializar_clientes_empleados()

    despiece = simular_despiece(lote, productos)
    venta, cc = simular_venta(clientes, empleados, productos)

    lista_ventas = [venta]
    lista_lotes = [lote]
    lista_productos = list(productos.values())
    lista_cuentas_cobrar = [cc]
    lista_clientes = list(clientes.values())

    generar_reportes_alertas(lista_ventas, lista_lotes, lista_productos, lista_cuentas_cobrar, lista_clientes)

    # Guardar todo
    for obj in [materia_prima, proveedor, lote] + list(empleados.values()) + list(clientes.values()) + lista_productos:
        db_manager.guardar_objeto(obj)

    db_manager.cerrar_conexion()
    print("✅ ERP Carnicería inicializado y datos persistidos correctamente.")

