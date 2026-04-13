import enum
from decimal import Decimal
from typing 

from sqlalchemy import Column, Integer, Numeric, Enum
from app.db.base import Base

class OrderStatus(str, enum.Enum):
    UNPAYED = "unpayied"
    PAID = "paid"
    REFUNDED = "refunded"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.UNPAYED, nullable=False)


