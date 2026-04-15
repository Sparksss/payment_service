import enum
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Numeric, String, Enum as SqlaEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.order import Order

class PaymentType(str, enum.Enum):
    CASH = "cash"
    ACQUIRING = "acquiring"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    payment_type: Mapped[PaymentType] = mapped_column(SqlaEnum(PaymentType), nullable=False, index=True)

    status: Mapped[PaymentStatus] = mapped_column(SqlaEnum(PaymentStatus), nullable=False, index=True)

    external_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True, index=True)

    error_message: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="payments")

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, type={self.payment_type}, status={self.status})>"
