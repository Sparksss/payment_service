from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class OrderStatus(str, Enum):
    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"

class OrderBase(BaseModel):
    total_amount: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=2,
        description="Сумма заказа (должна быть больше 0)"
    )

class OrderCreate(BaseModel):
    pass

class PaymentShortInfo(BaseModel):
    id: int
    amount: Decimal
    status: str
    payment_type: str

    model_config = ConfigDict(from_attributes=True)

class OrderRead(OrderBase):
    id: int
    status: OrderStatus

    model_config = ConfigDict(from_attributes=True)
    