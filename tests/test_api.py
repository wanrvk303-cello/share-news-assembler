import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db, engine, Base


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/users", json={"username": "testuser"})
        assert res.status_code == 200
        data = res.json()
        assert data["username"] == "testuser"
        assert "id" in data


@pytest.mark.asyncio
async def test_duplicate_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/users", json={"username": "dup"})
        res = await client.post("/api/users", json={"username": "dup"})
        assert res.status_code == 409


@pytest.mark.asyncio
async def test_add_holding():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user = (await client.post("/api/users", json={"username": "h1"})).json()
        res = await client.post(f"/api/users/{user['id']}/holdings", json={"ticker": "AAPL"})
        assert res.status_code == 200
        assert res.json()["ticker"] == "AAPL"


@pytest.mark.asyncio
async def test_duplicate_holding():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user = (await client.post("/api/users", json={"username": "h2"})).json()
        await client.post(f"/api/users/{user['id']}/holdings", json={"ticker": "MSFT"})
        res = await client.post(f"/api/users/{user['id']}/holdings", json={"ticker": "MSFT"})
        assert res.status_code == 409


@pytest.mark.asyncio
async def test_delete_holding():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user = (await client.post("/api/users", json={"username": "h3"})).json()
        holding = (await client.post(f"/api/users/{user['id']}/holdings", json={"ticker": "GOOGL"})).json()
        res = await client.delete(f"/api/users/{user['id']}/holdings/{holding['id']}")
        assert res.status_code == 200
        holdings = (await client.get(f"/api/users/{user['id']}/holdings")).json()
        assert len(holdings) == 0


@pytest.mark.asyncio
async def test_list_holdings():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user = (await client.post("/api/users", json={"username": "h4"})).json()
        await client.post(f"/api/users/{user['id']}/holdings", json={"ticker": "AAPL"})
        await client.post(f"/api/users/{user['id']}/holdings", json={"ticker": "MSFT"})
        res = await client.get(f"/api/users/{user['id']}/holdings")
        assert res.status_code == 200
        assert len(res.json()) == 2


@pytest.mark.asyncio
async def test_ticker_search():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/tickers/search?q=AAPL")
        assert res.status_code == 200
        data = res.json()
        assert any(t["ticker"] == "AAPL" for t in data)


@pytest.mark.asyncio
async def test_market_news_empty():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/news/market")
        assert res.status_code == 200
        assert res.json()["total"] == 0


@pytest.mark.asyncio
async def test_personal_news_empty():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user = (await client.post("/api/users", json={"username": "n1"})).json()
        res = await client.get(f"/api/news/personal/{user['id']}")
        assert res.status_code == 200
        assert res.json()["total"] == 0


@pytest.mark.asyncio
async def test_stock_news_empty():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/news/stock/TSLA")
        assert res.status_code == 200
        assert res.json()["total"] == 0


@pytest.mark.asyncio
async def test_unknown_ticker_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user = (await client.post("/api/users", json={"username": "unk"})).json()
        res = await client.post(f"/api/users/{user['id']}/holdings", json={"ticker": "ZZZZZ"})
        assert res.status_code == 400


@pytest.mark.asyncio
async def test_update_holding():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user = (await client.post("/api/users", json={"username": "u1"})).json()
        holding = (await client.post(f"/api/users/{user['id']}/holdings", json={"ticker": "AAPL"})).json()
        res = await client.put(
            f"/api/users/{user['id']}/holdings/{holding['id']}",
            json={"name": "My Apple"}
        )
        assert res.status_code == 200
        assert res.json()["name"] == "My Apple"


@pytest.mark.asyncio
async def test_user_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/users/99999")
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_holding_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user = (await client.post("/api/users", json={"username": "nf1"})).json()
        res = await client.delete(f"/api/users/{user['id']}/holdings/99999")
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_ticker_search_empty():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/tickers/search?q=ZZZZZ")
        assert res.status_code == 200
        assert len(res.json()) == 0


@pytest.mark.asyncio
async def test_ticker_search_partial():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/tickers/search?q=APP")
        assert res.status_code == 200
        data = res.json()
        assert any(t["ticker"] == "AAPL" for t in data)


@pytest.mark.asyncio
async def test_holding_update_name_only():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user = (await client.post("/api/users", json={"username": "u2"})).json()
        holding = (await client.post(f"/api/users/{user['id']}/holdings", json={"ticker": "MSFT"})).json()
        original_ticker = holding["ticker"]
        res = await client.put(
            f"/api/users/{user['id']}/holdings/{holding['id']}",
            json={"name": "My Microsoft"}
        )
        assert res.status_code == 200
        assert res.json()["ticker"] == original_ticker
        assert res.json()["name"] == "My Microsoft"


@pytest.mark.asyncio
async def test_personal_news_with_holdings():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user = (await client.post("/api/users", json={"username": "pn1"})).json()
        await client.post(f"/api/users/{user['id']}/holdings", json={"ticker": "AAPL"})
        res = await client.get(f"/api/news/personal/{user['id']}")
        assert res.status_code == 200
        assert "items" in res.json()


@pytest.mark.asyncio
async def test_stock_news_with_ticker():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/news/stock/AAPL")
        assert res.status_code == 200
        assert "items" in res.json()


@pytest.mark.asyncio
async def test_market_news_pagination():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/news/market?page=1&page_size=10")
        assert res.status_code == 200
        data = res.json()
        assert data["page"] == 1
        assert data["page_size"] == 10


@pytest.mark.asyncio
async def test_stats_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/stats")
        assert res.status_code == 200
        data = res.json()
        assert "users" in data
        assert "holdings" in data
        assert "news_items" in data
        assert "stock_mappings" in data


@pytest.mark.asyncio
async def test_create_multiple_users():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/api/users", json={"username": "mu1"})
        await client.post("/api/users", json={"username": "mu2"})
        res1 = await client.get("/api/users/1")
        res2 = await client.get("/api/users/2")
        assert res1.status_code == 200
        assert res2.status_code == 200


@pytest.mark.asyncio
async def test_holding_update_nonexistent():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user = (await client.post("/api/users", json={"username": "un1"})).json()
        res = await client.put(
            f"/api/users/{user['id']}/holdings/99999",
            json={"name": "Test"}
        )
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_ticker_search_limit():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/tickers/search?q=A")
        assert res.status_code == 200
        data = res.json()
        assert len(data) <= 20


@pytest.mark.asyncio
async def test_news_age_filter_24h():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/news/market?age_filter=24h")
        assert res.status_code == 200
        assert "items" in res.json()


@pytest.mark.asyncio
async def test_news_age_filter_7d():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/news/market?age_filter=7d")
        assert res.status_code == 200
        assert "items" in res.json()
