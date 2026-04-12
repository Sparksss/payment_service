from app.services.strategies.base import PaymentStrategy
from app.models.payments import Payment, PaymentStatus

class AcquiringPaymentStrategy(PaymentStrategy):
    def __init__(self, db_session, bank_client):
        self.db = db_session
        self.bank_client = bank_client
        super().__init__()
    
    async def deposit(self, order, amount):
        transaction_id = await self.bank_client.process_payment(order.id, amount)
        payment = Payment(
            order_id=order.id,
            amount=amount,
            payment_type=PaymentStrategy.ACQUIRING,
            transaction_id=transaction_id
        )
        self.db.add(payment)
        return payment
    
    async def refund(self, payment: Payment) -> bool:
        success = await self.bank_client.refund_payment(payment.transaction_id)
        if success:
            payment.status = PaymentStatus.REFUNDED
            self.db.add(payment)
            
        return success