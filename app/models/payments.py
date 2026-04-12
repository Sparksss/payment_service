import enum
from sqlalchemy import Column, Integer, Numeric, String, ForegnKey, Enum
from app.db.base import Base

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

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForegnKey("orders.id"), nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    external_id = Column(String, nullable=True, index=True)
    error_code = Column(String, nullable=True)
    error_massage = Column(String, nullable=True)
