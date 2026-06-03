import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Holding
from app.schemas import UserCreate, UserResponse, HoldingCreate, HoldingResponse, HoldingUpdate
from app.tickers import COMMON_TICKERS

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/users", response_model=UserResponse)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.username == data.username))
    if existing.scalar_one_or_none():
        logger.warning(f"Duplicate username attempt: {data.username}")
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(username=data.username)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info(f"Created user: {user.id} ({user.username})")
    return user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/tickers/search")
async def search_tickers(q: str = ""):
    q_upper = q.upper()
    results = []
    for ticker, name in COMMON_TICKERS.items():
        if q_upper in ticker or q_upper in name.upper():
            results.append({"ticker": ticker, "name": name})
            if len(results) >= 20:
                break
    return results


@router.post("/users/{user_id}/holdings", response_model=HoldingResponse)
async def add_holding(user_id: int, data: HoldingCreate, db: AsyncSession = Depends(get_db)):
    user_result = await db.execute(select(User).where(User.id == user_id))
    if not user_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")

    ticker_upper = data.ticker.upper()
    if ticker_upper not in COMMON_TICKERS and not data.name:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown ticker '{ticker_upper}'. Provide a name or use a known ticker."
        )

    existing = await db.execute(
        select(Holding).where(Holding.user_id == user_id, Holding.ticker == ticker_upper)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Already holding {ticker_upper}")

    name = data.name or COMMON_TICKERS.get(ticker_upper, ticker_upper)
    holding = Holding(user_id=user_id, ticker=ticker_upper, name=name)
    db.add(holding)
    await db.commit()
    await db.refresh(holding)
    return holding


@router.get("/users/{user_id}/holdings", response_model=list[HoldingResponse])
async def list_holdings(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Holding).where(Holding.user_id == user_id).order_by(Holding.added_at.desc())
    )
    return result.scalars().all()


@router.put("/users/{user_id}/holdings/{holding_id}", response_model=HoldingResponse)
async def update_holding(
    user_id: int,
    holding_id: int,
    data: HoldingUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Holding).where(Holding.id == holding_id, Holding.user_id == user_id)
    )
    holding = result.scalar_one_or_none()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    if data.name is not None:
        holding.name = data.name
    await db.commit()
    await db.refresh(holding)
    return holding


@router.delete("/users/{user_id}/holdings/{holding_id}")
async def delete_holding(user_id: int, holding_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Holding).where(Holding.id == holding_id, Holding.user_id == user_id)
    )
    holding = result.scalar_one_or_none()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    await db.delete(holding)
    await db.commit()
    return {"detail": "Holding deleted"}
