from .base import DomainException

class VentaException(DomainException):
    pass

class VentaCerradaError(VentaException):
    pass

class VentaSinItemsError(VentaException):
    pass

class VentaFueraDePlazoError(VentaException):
    pass

# core/domain/exceptions/venta_exceptions.py

class ClienteSinCreditoError(Exception):
    """Se intenta vender a crédito a un cliente sin crédito habilitado"""
    pass

class VentaNoCancelableError(Exception):
    """La venta no puede cancelarse por su estado o efectos posteriores."""
    pass

class VentaError(Exception):
    """Excepción base del dominio Venta."""
    pass


class VentaNoCancelableError(VentaError):
    pass


class PagoExcesivoError(VentaError):
    """
    Se lanza cuando se intenta registrar un pago
    mayor al saldo pendiente de la venta.
    """
    pass
