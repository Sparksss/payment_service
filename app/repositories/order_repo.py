from typing import Optional
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.payments import Payment, PaymentStatus

class OrderRepository:
    async def get_by_id(self, db: AsyncSession, order_id: int) -> Optional[Order]:
        result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalars().first()
    
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
            .where(Payment.order_id == order_id,
            Payment.status == PaymentStatus.COMPLETED)
        )
        result = await db.execute(query)
        return Decimal(result.scalar())
    
    async def list_orders(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(
            select(Order)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()