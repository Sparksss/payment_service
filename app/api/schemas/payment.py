from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum

class PaymentType(str, Enum):
    CASH = "cash"
    ACQUIRING = "acquiring"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REFUNDED = "refunded"
    FAILED = "failed"

class PaymentCreate(BaseModel):
    order_id: int
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    payment_type: PaymentType = Field(..., description="Cash or Acquiring")

    @field_validator("amount")
    @classmethod
    def validate_amount_precision(cls, v: Decimal) -> Decimal:
        if v.as_tuple().exponent < -2:
            raise ValueError("Сумма не может иметь более 2 знаков после запятой")
        return v

class PaymentRead(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    payment_type: PaymentType
    status: PaymentStatus
    external_id: Optional[str] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PaymentRefund(BaseModel):
    payment_id: int