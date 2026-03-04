#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos de prueba.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.persistencia import db_manager
from app.infraestructura.persistence.orm.modelos import ProductoElaborado, MateriaPrima, Proveedor, Cliente, Empleado
from datetime import date

def inicializar_datos():
    """Inicializa la base de datos con datos básicos."""
    print("📦 Inicializando base de datos con datos de prueba...")
    
    with db_manager.get_session() as session:
        # Crear productos básicos
        productos = [
            ProductoElaborado(nombre="Vacio", precio_venta=12.99, stock_actual=50.0),
            ProductoElaborado(nombre="Bife de Chorizo", precio_venta=15.50, stock_actual=30.0),
            ProductoElaborado(nombre="Nalga", precio_venta=7.00, stock_actual=40.0),
            ProductoElaborado(nombre="Asado", precio_venta=10.99, stock_actual=25.0),
            ProductoElaborado(nombre="Costillas", precio_venta=9.25, stock_actual=35.0),
        ]
        
        for producto in productos:
            session.merge(producto)
        
        # Crear cliente básico
        cliente = Cliente(nombre="Cliente General", telefono="+5491112345678")
        session.merge(cliente)
        
        # Crear empleado básico
        empleado = Empleado(nombre="Carlos Gómez")
        session.merge(empleado)
        
        session.commit()
        print(f"✅ Datos inicializados: {len(productos)} productos creados")
        print("✅ Cliente y empleado creados")
    
    print("🎯 Base de datos lista para usar")

if __name__ == "__main__":
    inicializar_datos()