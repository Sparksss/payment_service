import enum
from decimal import Decimal
from typing import List, TYPE_CHECKING

from sqlalchemy import Numeric, Enum as SqlaEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.payments import Payment

class OrderStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    ARCHIVED = "archived"

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(SqlaEnum(OrderStatus), default=OrderStatus.UNPAID, nullable=False)

    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="order")
