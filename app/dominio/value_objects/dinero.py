# app/dominio/value_objects/dinero.py
from decimal import Decimal
from ..exceptions import ValorInvalidoError

class Dinero:
    """
    Value Object para manejo seguro de operaciones monetarias.
    Inmutable y con validaciones.
    """
    
    def __init__(self, monto, moneda='ARS'):
        # Validar monto no negativo
        if monto < 0:
            raise ValorInvalidoError("El monto no puede ser negativo")
        
        # Usar Decimal para precisión en cálculos financieros
        self._monto = Decimal(str(monto)).quantize(Decimal('0.01'))
        self._moneda = moneda
    
    @property
    def monto(self):
        return float(self._monto)
    
    @property
    def moneda(self):
        return self._moneda
    
    def __add__(self, other):
        """Suma dos cantidades de dinero de la misma moneda"""
        if not isinstance(other, Dinero):
            raise TypeError("Solo se puede sumar Dinero con Dinero")
        
        if self.moneda != other.moneda:
            raise ValorInvalidoError(f"No se pueden sumar {self.moneda} con {other.moneda}")
        
        return Dinero(float(self._monto + other._monto), self.moneda)
    
    def __sub__(self, other):
        """Resta dos cantidades de dinero"""
        if not isinstance(other, Dinero):
            raise TypeError("Solo se puede restar Dinero con Dinero")
        
        if self.moneda != other.moneda:
            raise ValorInvalidoError(f"No se pueden restar {self.moneda} con {other.moneda}")
        
        return Dinero(float(self._monto - other._monto), self.moneda)
    
    def __mul__(self, factor):
        """Multiplica dinero por un escalar"""
        if not isinstance(factor, (int, float, Decimal)):
            raise TypeError("Solo se puede multiplicar por número")
        
        return Dinero(float(self._monto * Decimal(str(factor))), self.moneda)
    
    def __rmul__(self, factor):
        """Multiplicación por la derecha"""
        return self.__mul__(factor)
    
    def __truediv__(self, divisor):
        """Divide dinero por un escalar"""
        if not isinstance(divisor, (int, float, Decimal)):
            raise TypeError("Solo se puede dividir por número")
        
        if divisor == 0:
            raise ValorInvalidoError("No se puede dividir por cero")
        
        return Dinero(float(self._monto / Decimal(str(divisor))), self.moneda)
    
    def __eq__(self, other):
        """Comparación de igualdad"""
        if not isinstance(other, Dinero):
            return False
        
        return (self._monto == other._monto) and (self.moneda == other.moneda)
    
    def __lt__(self, other):
        """Comparación menor que"""
        if not isinstance(other, Dinero):
            raise TypeError("Solo se puede comparar Dinero con Dinero")
        
        if self.moneda != other.moneda:
            raise ValorInvalidoError("Monedas diferentes no comparables")
        
        return self._monto < other._monto
    
    def __str__(self):
        """Representación amigable para usuario"""
        if self.moneda == 'ARS':
            return f"${self.monto:,.2f}"
        else:
            return f"{self.monto:,.2f} {self.moneda}"
    
    def __repr__(self):
        """Representación para debugging"""
        return f"Dinero(monto={self.monto}, moneda='{self.moneda}')"
    
    @classmethod
    def zero(cls, moneda='ARS'):
        """Factory method para crear dinero cero"""
        return cls(0.0, moneda)
    
    @classmethod
    def from_string(cls, monto_str, moneda='ARS'):
        """Crear dinero desde string"""
        try:
            monto = float(monto_str)
            return cls(monto, moneda)
        except ValueError:
            raise ValorInvalidoError(f"Formato inválido para monto: {monto_str}")