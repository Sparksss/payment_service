import logging
from decimal import Decimal
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.payments import Payment, PaymentStatus, PaymentType
from app.api.schemas.payment import PaymentCreate
from app.repositories.order_repo import OrderRepository
from app.repositories.payment_repo import PaymentRepository
from app.services.strategies.base import PaymentStrategy

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(
        self, 
        order_repo: OrderRepository, 
        payment_repo: PaymentRepository, 
        strategies: Dict[PaymentType, PaymentStrategy]
    ):
        self.order_repo = order_repo
        self.payment_repo = payment_repo
        self._strategies = strategies

    async def create_deposit(self, db: AsyncSession, data: PaymentCreate) -> Payment:
        async with db.begin():
            order = await self.order_repo.get_by_id_for_update(db, data.order_id)
            if not order:
                raise ValueError("Заказ не найден")

            total_paid = await self.order_repo.get_total_paid_amount(db, order.id)
            if total_paid + data.amount > order.total_amount:
                raise ValueError("Сумма платежей превышает стоимость заказа")
            
            strategy = self._strategies.get(data.payment_type)
            if not strategy:
                raise ValueError(f"Тип оплаты {data.payment_type} не поддерживается")

            payment = await strategy.deposit(db, order, data.amount)
            
            if payment.status == PaymentStatus.COMPLETED:
                await self.order_repo.sync_order_status(db, order.id)

            return payment

    async def refund_payment(self, db: AsyncSession, payment_id: int) -> Payment:
        async with db.begin():
            payment = await self.payment_repo.get_by_id(db, payment_id)
            
            if not payment or payment.status != PaymentStatus.COMPLETED:
                raise ValueError("Платеж не найден или не подтвержден для возврата")

            strategy = self._strategies.get(payment.payment_type)
            if not strategy:
                raise ValueError(f"Стратегия для {payment.payment_type} не найдена")

            success = await strategy.refund(db, payment)
            if not success:
                raise ValueError("Банк отклонил операцию возврата")

            await self.order_repo.sync_order_status(db, payment.order_id)
            
            return payment

    async def process_bank_callback(self, db: AsyncSession, external_id: str, status: PaymentStatus):
        async with db.begin(): 
            payment = await self.payment_repo.get_by_external_id(db, external_id)
            if not payment:
                logger.warning(f"Получен callback для неизвестного платежа: {external_id}")
                return
            
            await self.payment_repo.update_status(db, payment.id, status)
            
            if status == PaymentStatus.COMPLETED or status == PaymentStatus.REFUNDED:
                await self.order_repo.sync_order_status(db, payment.order_id)