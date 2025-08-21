from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from pgvector.sqlalchemy import Vector
from ..db.session import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(64), index=True, nullable=True)
    source = Column(String(64), nullable=True)  # e.g., email, call_transcript, crm_note
    title = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
