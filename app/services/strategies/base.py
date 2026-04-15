from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payments import Payment
from app.models.order import Order
from decimal import Decimal

class PaymentStrategy(ABC):
    @abstractmethod
    async def deposit(self, db: AsyncSession, order: Order, amount: Decimal) -> Payment:
        pass

    @abstractmethod
    async def refund(self, db: AsyncSession, payment: Payment) -> bool:
        pass