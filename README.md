# Stock News Aggregator

RSS-driven stock news aggregator with real-time UI. Monitors finance RSS feeds and presents curated news items grouped by user holdings, individual stocks, or market-wide events.

## Features

- **Personal View**: News related to your stock holdings
- **Per-Stock View**: News for a single selected stock
- **Market View**: Broad market news
- Age filter (24h / 7d / All)
- Ticker badges and matched tags
- Dark mode UI
- Keyboard shortcuts (1/2/3 for views, R for refresh)
- Automatic RSS feed polling every 30 minutes
- News deduplication
- 100+ US stock tickers supported

## Setup

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
python run.py
```

Open http://localhost:8000

## API Endpoints

- `POST /api/users` - Create user
- `GET /api/users/{id}` - Get user
- `POST /api/users/{id}/holdings` - Add holding
- `GET /api/users/{id}/holdings` - List holdings
- `PUT /api/users/{id}/holdings/{id}` - Update holding
- `DELETE /api/users/{id}/holdings/{id}` - Delete holding
- `GET /api/tickers/search?q=` - Search tickers
- `GET /api/news/personal/{user_id}` - Personal news
- `GET /api/news/stock/{ticker}` - Stock news
- `GET /api/news/market` - Market news
- `POST /api/ingest` - Trigger RSS ingestion
- `GET /api/health` - Health check

## Running Tests

```bash
pytest
```

## Architecture

- **Backend**: FastAPI + SQLAlchemy (async) + SQLite
- **RSS Ingestion**: feedparser + APScheduler (30min polling)
- **Frontend**: Vanilla JS + CSS (dark theme)
- **Ticker Mapping**: Keyword + fuzzy name matching
