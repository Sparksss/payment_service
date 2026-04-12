from abc import ABC, abstractmethod

from app.models.payments import Payment


class PaymentStrategy(ABC):
    @abstractmethod
    async def deposit(self, order, amount) -> Payment:
        pass

    @abstractmethod
    async def refund(self, payment: Payment) -> bool:
        pass