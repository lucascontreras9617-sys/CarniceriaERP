# app/infraestructura/persistence/repositorios/lote_repository_sqlalchemy.py
"""
Repositorio SQLAlchemy para Lote - Según estructura hexagonal target
"""
from sqlalchemy.orm import Session

# Import desde el ORM en la nueva ubicación
from app.infraestructura.persistence.orm.modelos import Lote as LoteORM

# Import desde el dominio hexagonal
from core.domain.entities.lote import Lote
from core.domain.value_objects.peso import Peso
from core.domain.exceptions import LoteNoEncontradoError

# Import desde los puertos de aplicación
from core.application.ports.lote_repository import LoteRepository


class LoteRepositorySQLAlchemy(LoteRepository):
    """
    Implementación concreta del repositorio de Lote
    Ubicación: app/infraestructura/persistence/repositorios/
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def obtener_por_id(self, lote_id: str) -> Lote:
        """Implementación del puerto - Obtiene lote o lanza excepción"""
        orm_lote = self.session.get(LoteORM, lote_id)
        
        if not orm_lote:
            raise LoteNoEncontradoError(f"Lote {lote_id} no encontrado")
        
        return self._mapear_orm_a_dominio(orm_lote)
    
    def guardar(self, lote: Lote) -> None:
        """Implementación del puerto - Guarda cambios"""
        orm_lote = self._mapear_dominio_a_orm(lote)
        self.session.merge(orm_lote)
        self.session.commit()
    
    # --- MÉTODOS DE MAPEO (PENDIENTE ver entidad Lote) ---
    
    def _mapear_orm_a_dominio(self, orm_lote: LoteORM) -> Lote:
        """
        Mapea modelo ORM a entidad de dominio
        NECESITO: core/domain/entities/lote.py para completar
        """
        # Esto es temporal - necesito tu entidad Lote
        return Lote(
            id=orm_lote.id,
            numero_tropa=orm_lote.num_tropa,
            peso_disponible=Peso.desde_kg(orm_lote.peso_restante),
            # ... otros atributos según tu entidad
        )
    
    def _mapear_dominio_a_orm(self, lote: Lote) -> LoteORM:
        """
        Mapea entidad de dominio a modelo ORM
        NECESITO: core/domain/entities/lote.py para completar
        """
        return LoteORM(
            id=lote.id,
            num_tropa=lote.numero_tropa,
            peso_restante=lote.peso_disponible.kg,
            # ... otros atributos
        )