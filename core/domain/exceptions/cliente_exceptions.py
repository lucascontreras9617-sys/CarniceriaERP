# core/domain/exceptions/cliente_exceptions.py

from core.domain.exceptions.base import DomainException


class ClienteException(DomainException):
    """Base para errores de cliente"""
    pass


class ClienteSinCreditoError(ClienteException):
    pass


class LimiteCreditoExcedidoError(ClienteException):
    pass

class PagoInvalidoError(Exception):
    pass
