from enum import Enum

class EstadoVenta(Enum):
    ABIERTA = "ABIERTA"
    CERRADA = "CERRADA"
    CANCELADA = "CANCELADA"
    SALDADA = "SALDADA"