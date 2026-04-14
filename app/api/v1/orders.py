from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.schemas.order import OrderRead


router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/{order_id}", response_model=OrderRead)
async def read_order(order_id: int ,db: AsyncSession = Depends(get_db)):
    db_order = await db.get(OrderRead, order_id)
    if not db_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return db_order

@router.post("/{order_id}/pay", response_model=OrderRead)
async def pay_order(order_id: int, db: AsyncSession = Depends(get_db)):