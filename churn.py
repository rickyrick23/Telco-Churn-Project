from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from ..db.session import Base


class ChurnFeatures(Base):
    __tablename__ = "churn_features"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(64), index=True, nullable=False)
    usage_drop_pct = Column(Float, nullable=True)
    billing_issue_count = Column(Integer, nullable=True)
    negative_sentiment_ratio = Column(Float, nullable=True)
    avg_ticket_resolution_days = Column(Float, nullable=True)
    monthly_bill = Column(Float, nullable=True)
    label_churned = Column(Integer, nullable=True)  # optional for supervised training
    created_at = Column(DateTime(timezone=True), server_default=func.now())
