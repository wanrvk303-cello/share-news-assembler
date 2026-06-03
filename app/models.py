import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    holdings = relationship("Holding", back_populates="user", cascade="all, delete-orphan")


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticker = Column(String(20), nullable=False)
    name = Column(String(200), nullable=True)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="holdings")

    __table_args__ = (
        UniqueConstraint("user_id", "ticker", name="uq_user_ticker"),
        Index("ix_holding_user", "user_id"),
        Index("ix_holding_ticker", "ticker"),
    )


class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    link = Column(Text, unique=True, nullable=False)
    teaser = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)
    source = Column(String(200), nullable=True)
    category = Column(String(50), nullable=False, default="stock_specific")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    mappings = relationship("NewsStockMapping", back_populates="news_item", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_news_category", "category"),
        Index("ix_news_created", "created_at"),
    )


class NewsStockMapping(Base):
    __tablename__ = "news_stock_mappings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    news_id = Column(Integer, ForeignKey("news_items.id"), nullable=False)
    ticker = Column(String(20), nullable=False)
    confidence = Column(Integer, default=100)

    news_item = relationship("NewsItem", back_populates="mappings")

    __table_args__ = (
        UniqueConstraint("news_id", "ticker", name="uq_news_ticker"),
        Index("ix_mapping_news", "news_id"),
        Index("ix_mapping_ticker", "ticker"),
    )
