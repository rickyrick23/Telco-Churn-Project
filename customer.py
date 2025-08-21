from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from ..db.session import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    region = Column(String(128), nullable=True)
    plan_type = Column(String(128), nullable=True)
    value_segment = Column(String(64), nullable=True)
    monthly_bill = Column(Float, nullable=True)
    churn_risk = Column(Float, nullable=True)
    churn_reason = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
