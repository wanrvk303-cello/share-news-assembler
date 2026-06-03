from app.mapper import extract_tickers_from_text, classify_item


def test_extract_ticker_exact():
    result = extract_tickers_from_text("Apple (AAPL) reported strong earnings")
    tickers = [t["ticker"] for t in result]
    assert "AAPL" in tickers


def test_extract_ticker_name():
    result = extract_tickers_from_text("Tesla surged today on news")
    tickers = [t["ticker"] for t in result]
    assert "TSLA" in tickers


def test_extract_multiple():
    result = extract_tickers_from_text("Both AAPL and MSFT rose today")
    tickers = [t["ticker"] for t in result]
    assert "AAPL" in tickers
    assert "MSFT" in tickers


def test_extract_none():
    result = extract_tickers_from_text("The market was mixed today")
    assert len(result) == 0


def test_classify_market_wide():
    assert classify_item([], "market_wide") == "market_wide"
    assert classify_item([{"ticker": "AAPL", "confidence": 100}], "market_wide") == "market_wide"


def test_classify_stock_specific():
    assert classify_item([{"ticker": "AAPL", "confidence": 100}, {"ticker": "MSFT", "confidence": 90}], "market_wide") == "stock_specific"
    assert classify_item([{"ticker": "AAPL", "confidence": 100}], "stock_specific") == "stock_specific"


def test_extract_fuzzy_name():
    result = extract_tickers_from_text("The company NVIDIA Corporation announced new chips")
    tickers = [t["ticker"] for t in result]
    assert "NVDA" in tickers


def test_extract_empty_text():
    result = extract_tickers_from_text("")
    assert result == []


def test_extract_none_text():
    result = extract_tickers_from_text(None)
    assert result == []


def test_classify_stock_feed_with_tickers():
    assert classify_item([{"ticker": "AAPL", "confidence": 100}], "stock_specific") == "stock_specific"
