from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HoldingCreate(BaseModel):
    ticker: str
    name: Optional[str] = None


class HoldingResponse(BaseModel):
    id: int
    ticker: str
    name: Optional[str]
    added_at: datetime

    class Config:
        from_attributes = True


class HoldingUpdate(BaseModel):
    name: Optional[str] = None


class UserCreate(BaseModel):
    username: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class NewsItemResponse(BaseModel):
    id: int
    title: str
    link: str
    teaser: Optional[str]
    published_at: Optional[datetime]
    source: Optional[str]
    category: str
    tickers: list[str] = []

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    items: list[NewsItemResponse]
    total: int
    page: int
    page_size: int
