"""
LoteRepository - Puerto hexagonal minimalista
REFACTORIZADO: Mantiene compatibilidad con uso real detectado

Análisis de uso real:
- guardar() ✅ SE USA (en registrar_venta.py)
- obtener_por_id() ❌ NO SE USA
- obtener_todos() ❌ NO SE USA  
- obtener_por_numero() ❌ NO SE USA
- actualizar_stock() ❌ NO SE USA
- obtener_con_stock() ❌ NO SE USA

Principios aplicados:
1. Interface Segregation (ISP) - No exponer métodos no usados
2. Hexagonal Architecture - Protocol para inyección limpia
3. Fail Fast - Lanzar excepciones de dominio temprano
"""
from typing import Protocol
from core.domain.entities.lote import Lote
from core.domain.exceptions import LoteNoEncontradoError


class LoteRepository(Protocol):
    """
    Puerto hexagonal minimalista - Solo métodos realmente usados
    
    Cambio de ABC a Protocol porque:
    - Mejor para inyección de dependencias (Duck Typing)
    - Permite verificación estática de tipos
    - Compatible con mockeo en tests sin herencia
    - Alineado con arquitectura hexagonal
    """
    
    def obtener_por_id(self, lote_id: str) -> Lote:
        """
        Obtiene un lote por su ID
        
        Args:
            lote_id: Identificador único del lote
            
        Returns:
            Lote: La entidad de dominio completa
            
        Raises:
            LoteNoEncontradoError: Si el lote no existe
            ValueError: Si lote_id es inválido (vacío, None, etc.)
            
        Nota:
            - NO retorna Optional, lanza excepción si no existe
            - Esto evita propagación de None y forcejea validación temprana
        """
        ...
    
    def guardar(self, lote: Lote) -> None:
        """
        Persiste un lote (crea o actualiza)
        
        Args:
            lote: Entidad de dominio a persistir
            
        Returns:
            None: Para evitar confusión con entidades mutadas
            
        Nota:
            - Retorna None (no la entidad) para evitar confusiones
            - La entidad ya está actualizada en memoria
            - Si necesitas ID generado, la entidad debe tenerlo antes
        """
        ...