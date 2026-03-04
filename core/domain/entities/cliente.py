from core.domain.exceptions.cliente_exceptions import (
    LimiteCreditoExcedidoError,
    ClienteSinCreditoError
)

from core.domain.exceptions.cliente_exceptions import PagoInvalidoError
class Cliente:
    def __init__(self, id: str, nombre: str, documento: str):
        self.id = id
        self.nombre = nombre
        self.documento = documento

    def validar_compra_a_credito(self, monto: float) -> None:
        raise NotImplementedError()
    

class ClienteContado(Cliente):
    def validar_compra_a_credito(self, monto: float) -> None:
        raise ClienteSinCreditoError()


class ClienteCrediticio(Cliente):
    def __init__(
        self,
        id: str,
        nombre: str,
        documento: str,
        limite_credito: float,
        saldo_deudor: float = 0.0
    ):
        super().__init__(id, nombre, documento)
        self.limite_credito = limite_credito
        self.saldo_deudor = saldo_deudor

    def registrar_deuda(self, monto: float) -> None:
        self.saldo_deudor += monto
   

    def validar_compra_a_credito(self, monto: float) -> None:
        if self.saldo_deudor + monto > self.limite_credito:
            raise LimiteCreditoExcedidoError()

    def pagar(self, monto: float) -> None:
        if monto <= 0 or monto > self.saldo_deudor:
            raise PagoInvalidoError()

        self.saldo_deudor -= monto

    def revertir_deuda(self, monto: float) -> None:
        self.saldo_deudor -= monto
        if self.saldo_deudor < 0:
         self.saldo_deudor = 0
 
    def tiene_pagos_registrados(self) -> bool:
        return self.saldo_deudor < self.limite_credito