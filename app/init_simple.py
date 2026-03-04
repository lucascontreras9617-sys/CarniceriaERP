#!/usr/bin/env python3
"""
Script de inicialización SIMPLE - Sin dependencias problemáticas
"""
import sys
import os
from datetime import date

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.persistencia import db_manager
from app.infraestructura.persistence.orm.modelos import ProductoElaborado, Cliente, Empleado

def init_simple():
    """Inicialización básica de la base de datos."""
    print("📦 Inicializando base de datos (versión simple)...")
    
    with db_manager.get_session() as session:
        # Crear productos básicos
        productos = [
            ProductoElaborado(nombre="Vacio", precio_venta=12.99, stock_actual=50.0, tipo="ROTACION"),
            ProductoElaborado(nombre="Bife de Chorizo", precio_venta=15.50, stock_actual=30.0, tipo="PREMIUM"),
            ProductoElaborado(nombre="Nalga", precio_venta=7.00, stock_actual=40.0, tipo="ROTACION"),
            ProductoElaborado(nombre="Asado", precio_venta=10.99, stock_actual=25.0, tipo="ROTACION"),
            ProductoElaborado(nombre="Costillas", precio_venta=9.25, stock_actual=35.0, tipo="ROTACION"),
        ]
        
        for p in productos:
            session.merge(p)
        
        # Crear cliente básico
        cliente = Cliente(nombre="Cliente General", telefono="+5491112345678", tipo="MINORISTA")
        session.merge(cliente)
        
        # Crear cliente mayorista
        cliente_mayorista = Cliente(
            nombre="Restaurante El Buen Sabor", 
            tipo="MAYORISTA", 
            limite_credito=5000.0
        )
        session.merge(cliente_mayorista)
        
        # Crear empleado básico
        empleado = Empleado(nombre="Carlos Gómez", legajo="EMP001", comision_pct=1.5)
        session.merge(empleado)
        
        session.commit()
        print(f"✅ {len(productos)} productos creados")
        print("✅ 2 clientes creados")
        print("✅ 1 empleado creado")
    
    print("🎯 Base de datos inicializada correctamente")

if __name__ == "__main__":
    init_simple()