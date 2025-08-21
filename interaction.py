from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.session import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(64), index=True, nullable=False)
    channel = Column(String(64), nullable=False)  # call, email, social, chat
    content = Column(Text, nullable=True)
    sentiment = Column(String(16), nullable=True)  # Positive/Neutral/Negative
    sentiment_score = Column(Float, nullable=True)
    topic = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
