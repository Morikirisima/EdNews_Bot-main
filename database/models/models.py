from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    shortened_content = Column(Text)
    source_url = Column(String(500), unique=True, nullable=False)
    image_url = Column(String(500))
    category = Column(String(100))
    status = Column(String(50), default="parsed")  # ← ИСПРАВИЛ defult на default
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    published_at = Column(DateTime(timezone=True))
    telegram_message_id = Column(Integer)

    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}')>"