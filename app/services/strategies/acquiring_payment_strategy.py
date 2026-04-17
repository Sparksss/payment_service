import logging
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.strategies.base import PaymentStrategy
from app.models.payments import Payment, PaymentStatus, PaymentType
from app.models.order import Order
from app.integrations.bank_client import BankAPIClient, BankAPIError

logger = logging.getLogger(__name__)

class AcquiringPaymentStrategy(PaymentStrategy):
    def __init__(self, bank_client: BankAPIClient):
        self.bank_client = bank_client
        super().__init__()
    
    async def deposit(self, db: AsyncSession, order: Order, amount: Decimal) -> Payment:
        payment = Payment(
            order_id=order.id,
            amount=amount,
            payment_type=PaymentType.ACQUIRING,
            status=PaymentStatus.PENDING,
        )
        db.add(payment)
        await db.flush()  
        try:
            external_id = await self.bank_client.process_payment(order.id, float(amount))
            payment.external_id = external_id
            
        except BankAPIError as e:
            payment.status = PaymentStatus.FAILED
            payment.error_message = f"Bank error: {str(e)}"
            logger.error(f"Payment failed for order {order.id}: {e}")
            
        except Exception as e:
            payment.error_message = f"Unexpected error: {str(e)}"
            logger.exception("Critical error during payment processing")

        return payment

    async def refund(self, db: AsyncSession, payment: Payment) -> bool:
        if not payment.external_id:
            payment.error_message = "Cannot refund: missing external_id"
            return False
            
        try:
            success = await self.bank_client.refund_payment(payment.external_id)
            if success:
                payment.status = PaymentStatus.REFUNDED
            else:
                payment.status = PaymentStatus.FAILED
                payment.error_message = "Bank declined refund"
            return bool(success)
        except Exception as e:
            payment.error_message = f"Refund error: {str(e)}"
            return False

    async def check_status(self, db: AsyncSession, payment: Payment) -> PaymentStatus:
        if not payment.external_id:
            return payment.status

        try:
            bank_status_raw = await self.bank_client.get_status(payment.external_id)
            
            new_status = self._map_bank_status(bank_status_raw)
            return new_status
        except Exception as e:
            logger.warning(f"Could not check status for payment {payment.id}: {e}")
            return payment.status

    def _map_bank_status(self, bank_status: str) -> PaymentStatus:
        mapping = {
            "SUCCESS": PaymentStatus.COMPLETED,
            "FAILED": PaymentStatus.FAILED,
            "IN_PROGRESS": PaymentStatus.PENDING
        }
        return mapping.get(bank_status, PaymentStatus.PENDING)