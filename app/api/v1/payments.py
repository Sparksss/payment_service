from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db
from app.schemas.payment import PaymentCreateSchema
from app.services.payment_service import PaymentService
from app.clients.bank_api import BankAPIClient

router = APIRouter(prefix="/payments", tags=["payments"])



@router.post("/")
async def create_payment(
    payload: PaymentCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    bank_client = BankAPIClient()
    service =  PaymentService(db, bank_client)

    return await service.create_deposit(payload.order_id, payload)