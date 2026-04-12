from app.services.strategies.cash_payment_strategy import CashPaymentStrategy
from app.services.strategies.acquiring_payment_ptrategy import AcquiringPaymentStrategy
from app.models.payments import PaymentType
from app.repositories.order_repo import OrderRepository


class PaymentService:
    def __init__(self, db_session, bank_client):
        self.db = db_session
        self._strategies = {
            PaymentType.CASH: CashPaymentStrategy(db_session=db_session),
            PaymentType.ACQUIRING: AcquiringPaymentStrategy(bank_client, bank_client)
        }

    async def create_deposit(self, order_id: int, payload: PaymentCreateSchema):
        order = await self.order_repo.get_by_id_for_update(self.db, order_id)

        if order.total_paid + payload.amount > order.total_amoiunt:
            raise ValidationError("Total payments exceed order amount")
        
        strategy = self._strategies.get(payload.payment_type)
        if not strategy:
            raise UnsupportedPaymentTypeError(f"Payment type {payload.payment_type} is not supported")
        
        payment = await strategy.deposit(order, payload.amoint)

        await self._update_order_status(order)

        await self.db.commit()
        return payment
    