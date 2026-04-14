from app.services.strategies.base import PaymentStrategy
from app.models.payments import Payment, PaymentStatus, PaymentType


class CashPaymentStrategy(PaymentStrategy):
    def __init__(self, db_session):
        self.db = db_session
        super().__init__()

    async def deposit(self, order, amount):
        payment = Payment(
                order_id=order.id,
                amount=amount,
                payment_type=PaymentType.CASH,
                external_id=None
        )
        self.db.add(payment)
        return payment
    
    async def refund(self, payment: Payment) -> bool:
        payment.status = PaymentStatus.REFUNDED
        self.db.add(payment)
        return True