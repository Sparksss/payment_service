from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel, Field
from decimal import Decimal

from app.db.session import get_db
from app.api.schemas.order import OrderRead, OrderCreate
from app.api.schemas.payment import PaymentCreate
from app.models.order import Order
from app.models.payments import PaymentType
from app.repositories.order_repo import OrderRepository
from app.services.payment_service import PaymentService
from app.api.v1.payments import get_payment_service

router = APIRouter(prefix="/orders", tags=["orders"])
order_repo = OrderRepository()

@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(order_in: OrderCreate, db: AsyncSession = Depends(get_db)):
    db_order = Order(total_amount=order_in.total_amount)
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order

@router.get("/", response_model=List[OrderRead])
async def list_orders(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await order_repo.list_orders(db, skip=skip, limit=limit)

@router.get("/{order_id}", response_model=OrderRead)
async def read_order(order_id: int, db: AsyncSession = Depends(get_db)):
    db_order = await order_repo.get_by_id(db, order_id)
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return db_order

class OrderPayPayload(BaseModel):
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    payment_type: PaymentType

@router.post("/{order_id}/pay", response_model=OrderRead)
async def pay_order(
    order_id: int,
    payload: OrderPayPayload,
    db: AsyncSession = Depends(get_db),
    payment_service: PaymentService = Depends(get_payment_service)
):
    payment_create = PaymentCreate(
        order_id=order_id,
        amount=payload.amount,
        payment_type=payload.payment_type
    )
    try:
        await payment_service.create_deposit(db, payment_create)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    db_order = await order_repo.get_by_id(db, order_id)
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return db_order