from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.strategies.base import PaymentStrategy
from app.models.payments import Payment, PaymentStatus, PaymentType
from app.models.order import Order

class CashPaymentStrategy(PaymentStrategy):
    async def deposit(self, db: AsyncSession, order: Order, amount: Decimal) -> Payment:
        payment = Payment(
            order_id=order.id,
            amount=amount,
            payment_type=PaymentType.CASH,
            status=PaymentStatus.COMPLETED,
            external_id=None
        )
        db.add(payment)
        return payment
    
    async def refund(self, db: AsyncSession, payment: Payment) -> bool:
        payment.status = PaymentStatus.REFUNDED
        db.add(payment)
        return True