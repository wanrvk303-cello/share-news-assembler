from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class HoldingCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20, description="Stock ticker symbol")
    name: Optional[str] = Field(None, max_length=200, description="Company name")


class HoldingResponse(BaseModel):
    id: int
    ticker: str
    name: Optional[str]
    added_at: datetime

    class Config:
        from_attributes = True


class HoldingUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200, description="Company name")


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=100, description="Username")


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
