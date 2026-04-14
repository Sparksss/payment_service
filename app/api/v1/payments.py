from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.schemas.payment import PaymentCreate, PaymentRead
from app.integrations.bank_client import BankAPIClient
from app.repositories.payment_repo import PaymentRepository
from app.repositories.order_repo import OrderRepository
from app.services.payment_service import PaymentService
from app.services.strategies.cash_payment_strategy import CashPaymentStrategy
from app.services.strategies.acquiring_payment_strategy import AcquiringPaymentStrategy
from app.models.payments import PaymentType

router = APIRouter(prefix="/payments", tags=["payments"])

async def get_payment_service() -> PaymentService:
    bank_client = BankAPIClient() 

    payment_repo = PaymentRepository()
    order_repo = OrderRepository()

    strategies = {
        PaymentType.CASH: CashPaymentStrategy(),
        PaymentType.ACQUIRING: AcquiringPaymentStrategy(bank_client)
    }

    return PaymentService(order_repo, payment_repo, strategies)


@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    service: PaymentService = Depends(get_payment_service)
):
    try:
        payment = await service.create_deposit(db, payload)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{payment_id}/refund", response_model=PaymentRead)
async def refund_payment(
        payment_id: int,
        db: AsyncSession = Depends(get_db),
        service: PaymentService = Depends(get_payment_service)
):
    try:
        return await service.refund_payment(db, payment_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )