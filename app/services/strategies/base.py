# app/services/strategies/base.py
from abc import ABC, abstractmethod
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payments import Payment, PaymentStatus
from app.models.order import Order

class PaymentStrategy(ABC):
    @abstractmethod
    async def deposit(self, db: AsyncSession, order: Order, amount: Decimal) -> Payment:
        pass

    @abstractmethod
    async def refund(self, db: AsyncSession, payment: Payment) -> bool:
        pass

    @abstractmethod
    async def check_status(self, db: AsyncSession, payment: Payment) -> PaymentStatus:
        pass