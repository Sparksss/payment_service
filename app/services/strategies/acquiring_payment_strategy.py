from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.strategies.base import PaymentStrategy
from app.models.payments import Payment, PaymentStatus, PaymentType
from app.models.order import Order
from app.integrations.bank_client import BankAPIClient

class AcquiringPaymentStrategy(PaymentStrategy):
    def __init__(self, bank_client: BankAPIClient):
        self.bank_client = bank_client
        super().__init__()
    
    async def deposit(self, db: AsyncSession, order: Order, amount: Decimal) -> Payment:
        external_id = await self.bank_client.process_payment(order.id, float(amount))
        payment = Payment(
            order_id=order.id,
            amount=amount,
            payment_type=PaymentType.ACQUIRING,
            status=PaymentStatus.PENDING,
            external_id=external_id
        )
        db.add(payment)
        return payment
    
    async def refund(self, db: AsyncSession, payment: Payment) -> bool:
        if not payment.external_id:
            return False
            
        success = await self.bank_client.refund_payment(payment.external_id)
        if success:
            payment.status = PaymentStatus.REFUNDED
            db.add(payment)
        else:
            payment.status = PaymentStatus.FAILED
            db.add(payment)
            
        return bool(success)