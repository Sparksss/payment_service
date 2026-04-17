# app/workers/tasks.py
import logging
from app.db.session import SessionLocal
from app.repositories.payment_repo import PaymentRepository
from app.services.strategies.factory import PaymentStrategyFactory

logger = logging.getLogger(__name__)

async def cleanup_pending_payments():
    """Фоновая задача для синхронизации зависших платежей"""
    async with SessionLocal() as db:
        repo = PaymentRepository(db)
        
        # 1. Берем платежи PENDING старше 15 минут
        stale_payments = await repo.get_stale_payments(minutes=15)
        
        for payment in stale_payments:
            try:
                strategy = PaymentStrategyFactory.get_strategy(payment.payment_type)
                
                new_status = await strategy.check_status(db, payment)
                
                if new_status != payment.status:
                    await repo.update_status(payment, new_status)
                    await db.commit()
                    logger.info(f"Payment {payment.id} reconciled to {new_status}")
                    
            except Exception as e:
                logger.error(f"Failed to reconcile payment {payment.id}: {str(e)}")
                await db.rollback()