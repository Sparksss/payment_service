from datetime import datetime, timedelta, timezone
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payments import Payment, PaymentStatus

class PaymentRepository:
    async def create(self, db: AsyncSession, payment: Payment) -> Payment:
        db.add(payment)
        await db.flush()
        return payment
    
    async def get_by_id(self, db: AsyncSession, payment_id: int) -> Optional[Payment]:
        result = await db.execute(
            select(Payment).where(Payment.id == payment_id)   
        )
        return result.scalars().first()
    
    async def get_by_external_id(self, db: AsyncSession, external_id: str) -> Optional[Payment]:
        result = await db.execute(
            select(Payment).where(Payment.external_id == external_id)
        )
        return result.scalars().first()
    
    async def update_status(self, db: AsyncSession, payment_id: int, status: PaymentStatus, error_message: Optional[str] = None):
        stmt = (
            update(Payment)
            .where(Payment.id == payment_id)
            .values(status=status, error_message=error_message)
        )
        await db.execute(stmt)

    async def get_stale_payments(self, db: AsyncSession, minutes: int = 15) -> List[Payment]:
        threshold = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        
        stmt = (
            select(Payment)
            .where(Payment.status == PaymentStatus.PENDING)
            .where(Payment.created_at <= threshold)
        )
        
        result = await db.execute(stmt)
        return list(result.scalars().all())