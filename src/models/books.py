from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from src.database import engine


Base = declarative_base()


class Roll(Base):
    __tablename__ = 'rolls'
    id = Column(Integer, primary_key=True, index=True)
    length = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    added_date = Column(DateTime, default=datetime.utcnow)
    removed_date = Column(DateTime, nullable=True)


class RollCreate(BaseModel):
    length: float
    weight: float


class RollResponse(BaseModel):
    id: int
    length: float
    weight: float
    added_date: datetime
    removed_date: Optional[datetime]

    class Config:
        orm_mode = True


Base.metadata.create_all(bind=engine)
