from sqlalchemy import Column, Integer, String, DateTime, JSON
from db.base import Base, utc_now


class AppSettings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    settings = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    task_text = Column(String, nullable=False)
    favorite = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)
