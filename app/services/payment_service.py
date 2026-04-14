from decimal import Decimal
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.order import OrderStatus
from app.api.schemas.payment import PaymentCreate
from app.models.order import Order
from app.models.payments import Payment, PaymentStatus, PaymentType
from app.repositories.order_repo import OrderRepository
from app.repositories.payment_repo import PaymentRepository
from app.services.strategies.base import PaymentStrategy

class PaymentService:
    def __init__(self, order_repo: OrderRepository, payment_repo: PaymentRepository, strategies: Dict[PaymentType, PaymentStrategy]):
        self.order_repo = order_repo
        self.payment_repo = payment_repo
        self._strategies = strategies

    async def create_deposit(self, db: AsyncSession, data: PaymentCreate) -> Payment:
        order = await self.order_repo.get_by_id_for_update(db, data.order_id)

        if not order:
            raise ValueError("Заказ не найден")

        total_paid = await self.order_repo.get_total_paid_amount(db, order.id)
        if total_paid + data.amount > order.total_amount:
            raise ValueError("Total payments exceed order amount")
        
        strategy = self._strategies.get(data.payment_type)
        if not strategy:
            raise ValueError(f"Тип оплаты {data.payment_type} не поддерживается")

        payment = await strategy.deposit(db, order, data.amount)

        if payment.status == PaymentStatus.COMPLETED:
            new_total_paid = total_paid + data.amount
            if new_total_paid >= order.total_amount:
                order.status = OrderStatus.PAID
            elif new_total_paid > 0:
                order.status = OrderStatus.PARTIALLY_PAID

        await db.commit()
        await db.refresh(payment)
        return payment

    async def refund_payment(self, db: AsyncSession, payment_id: int) -> Payment:
        payment = await self.payment_repo.get_by_id(db, payment_id)
        if not payment or payment.status not in (PaymentStatus.COMPLETED, PaymentStatus.PENDING): # Can be PENDING or COMPLETED ? Usually only COMPLETED can be refunded.
            raise ValueError("Платеж не найден или не может быть возвращен")

        order = await self.order_repo.get_by_id_for_update(db, payment.order_id)
        
        strategy = self._strategies.get(payment.payment_type)
        if not strategy:
            raise ValueError(f"Тип оплаты {payment.payment_type} не поддерживается")

        success = await strategy.refund(db, payment)
        if not success:
            raise ValueError("Ошибка возврата платежа")

        total_paid_after = await self.order_repo.get_total_paid_amount(db, order.id)

        if total_paid_after == 0:
            order.status = OrderStatus.UNPAID
        elif total_paid_after < order.total_amount:
            order.status = OrderStatus.PARTIALLY_PAID

        await db.commit()
        await db.refresh(payment)
        return payment
