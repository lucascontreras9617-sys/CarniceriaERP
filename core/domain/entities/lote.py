"""
Lote - Entidad de dominio para lotes
"""
from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from uuid import uuid4
from ..value_objects.peso import Peso
from ..value_objects.dinero import Dinero

@dataclass
class Lote:
    """Lote de materia prima o producto"""
    id: str
    numero_tropa: str
    producto_nombre: str
    peso_total: Peso
    peso_disponible: Peso
    costo_total: Dinero
    fecha_ingreso: date
    proveedor: Optional[str] = None
    fecha_vencimiento: Optional[date] = None
    estado: str = "DISPONIBLE"  # DISPONIBLE, PROCESADO, VENDIDO
    
    def __post_init__(self):
        if self.peso_disponible.valor > self.peso_total.valor:
            raise ValueError("El peso disponible no puede ser mayor al total")
    
    @property
    def costo_por_kg(self) -> Dinero:
        """Calcula costo por kilogramo"""
        if self.peso_total.valor == 0:
            return Dinero(0)
        return self.costo_total / self.peso_total.valor
    
    def consumir(self, peso_a_consumir: Peso) -> Peso:
        """Consume una cantidad del lote"""
        if self.estado != "DISPONIBLE":
            raise ValueError(f"Lote {self.id} no está disponible")
        
        if peso_a_consumir.valor > self.peso_disponible.valor:
            raise ValueError(
                f"No hay suficiente peso disponible. "
                f"Disponible: {self.peso_disponible}, Solicitado: {peso_a_consumir}"
            )
        
        self.peso_disponible = self.peso_disponible - peso_a_consumir
        
        if self.peso_disponible.valor == 0:
            self.estado = "PROCESADO"
        
        return peso_a_consumir
    
    @classmethod
    def crear_nuevo(cls, numero_tropa: str, producto: str, peso_kg: float, 
                   costo_total: float, proveedor: str = None) -> 'Lote':
        """Factory method para crear nuevo lote"""
        return cls(
            id=str(uuid4()),
            numero_tropa=numero_tropa,
            producto_nombre=producto,
            peso_total=Peso.desde_kg(peso_kg),
            peso_disponible=Peso.desde_kg(peso_kg),
            costo_total=Dinero.desde_monto(costo_total),
            fecha_ingreso=date.today(),
            proveedor=proveedor,
            estado="DISPONIBLE"
        )
    
    def __str__(self) -> str:
        return f"Lote {self.numero_tropa} - {self.producto_nombre} - {self.peso_disponible} disp."

