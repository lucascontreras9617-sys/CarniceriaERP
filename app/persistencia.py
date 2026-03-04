# app/persistencia.py (VERSIÓN INTEGRADA COMPLETA)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from contextlib import contextmanager
import os
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
import json

# Ruta ABSOLUTA a la base de datos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'carniceria_orm.db')

# Asegurar que el directorio existe
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

class DBManager:
    """Gestiona la conexión, la creación de tablas y las operaciones CRUD usando SQLAlchemy ORM."""
    
    def __init__(self):
        self._create_engine_and_tables(DB_PATH)
        self.SessionFactory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.Session = scoped_session(self.SessionFactory)
        print(f"✓ Base de datos ORM y tablas inicializadas en: {DB_PATH}")
        print(f"✓ Ruta: {DB_PATH}")

    def _create_engine_and_tables(self, db_path: str):
        """Método interno para crear el engine y las tablas."""
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            echo=False,
            pool_pre_ping=True,
            connect_args={'check_same_thread': False}
        )
        from app.infraestructura.persistence.orm.modelos import Base
        Base.metadata.create_all(self.engine)
        return self.engine

    @contextmanager
    def get_session(self) -> Session:
        """Context manager para manejo automático de sesiones"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"❌ Error en sesión: {e}")
            raise
        finally:
            session.close()

    def guardar_objeto(self, obj):
        """Método genérico para guardar cualquier objeto mapeado."""
        with self.get_session() as session:
            session.merge(obj)

    # --- Funciones de Carga Específicas ---
    def obtener_por_atributo(self, modelo, atributo: str, valor):
        """Carga un objeto específico por un atributo y su valor."""
        with self.get_session() as session:
           return session.query(modelo).filter(getattr(modelo, atributo) == valor).first()



    # --- NUEVOS MÉTODOS PARA CAJA Y REPORTES ---
    def obtener_caja_por_fecha(self, fecha: date):
        """Obtiene la caja de una fecha específica."""
        from .modelos import Caja
        with self.get_session() as session:
            return session.query(Caja).filter_by(fecha=fecha).first()

    def obtener_ventas_por_fecha(self, fecha_inicio: date, fecha_fin: date = None):
        """Obtiene ventas en un rango de fechas."""
        from .modelos import Venta
        with self.get_session() as session:
            query = session.query(Venta).filter(Venta.fecha >= fecha_inicio)
            if fecha_fin:
                query = query.filter(Venta.fecha <= fecha_fin)
            return query.all()

    def obtener_gastos_por_fecha(self, fecha_inicio: date, fecha_fin: date = None):
        """Obtiene gastos en un rango de fechas."""
        from .modelos import Gasto
        with self.get_session() as session:
            query = session.query(Gasto).filter(Gasto.fecha >= fecha_inicio)
            if fecha_fin:
                query = query.filter(Gasto.fecha <= fecha_fin)
            return query.all()

    def obtener_ventas_del_dia(self):
        """Obtiene ventas del día actual."""
        from .modelos import Venta
        with self.get_session() as session:
            return session.query(Venta).filter_by(fecha=date.today()).all()

    def obtener_gastos_del_dia(self):
        """Obtiene gastos del día actual."""
        from .modelos import Gasto
        with self.get_session() as session:
            return session.query(Gasto).filter_by(fecha=date.today()).all()

    def cerrar_conexion(self):
        """Cierra las sesiones."""
        self.Session.remove()
        print("✓ Módulo de Persistencia ORM cerrado.")

# Instancia global del DBManager
db_manager = DBManager()