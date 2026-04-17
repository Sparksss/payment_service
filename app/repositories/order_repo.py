from typing import Optional, cast
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
from app.models.payments import Payment, PaymentStatus

class OrderRepository:

    async def get_by_id_for_update(self, db: AsyncSession, order_id: int) -> Optional[Order]:
        result = await db.execute(
            select(Order)
            .where(Order.id == order_id)
            .with_for_update()
        )
        return result.scalars().first()

    async def get_total_paid_amount(self, db: AsyncSession, order_id: int) -> Decimal:
        query = (
            select(func.coalesce(func.sum(Payment.amount), 0))
            .where(
                Payment.order_id == order_id,
                Payment.status == PaymentStatus.COMPLETED
            )
        )
        result = await db.execute(query)
        val = cast(Optional[Decimal | float], result.scalar())
        
        if val is None:
            return Decimal(0)
        return Decimal(str(val))

    async def sync_order_status(self, db: AsyncSession, order_id: int) -> Optional[Order]:
        order = await self.get_by_id_for_update(db, order_id)
        if not order:
            return None

        total_paid = await self.get_total_paid_amount(db, order_id)

        if total_paid >= order.total_amount:
            order.status = OrderStatus.PAID
        elif total_paid > 0:
            order.status = OrderStatus.PARTIALLY_PAID
        else:
            order.status = OrderStatus.UNPAID
            
        return order