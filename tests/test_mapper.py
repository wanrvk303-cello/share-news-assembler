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
    result = extract_tickers_from_text("The company NVIDIA announced new chips")
    tickers = [t["ticker"] for t in result]
    assert "NVDA" in tickers


def test_extract_short_name_apple():
    result = extract_tickers_from_text("Apple reported strong iPhone sales")
    tickers = [t["ticker"] for t in result]
    assert "AAPL" in tickers


def test_extract_short_name_google():
    result = extract_tickers_from_text("Google Cloud revenue grew 30%")
    tickers = [t["ticker"] for t in result]
    assert "GOOGL" in tickers


def test_extract_short_name_facebook():
    result = extract_tickers_from_text("Facebook parent Meta reported earnings")
    tickers = [t["ticker"] for t in result]
    assert "META" in tickers


def test_extract_empty_text():
    result = extract_tickers_from_text("")
    assert result == []


def test_extract_none_text():
    result = extract_tickers_from_text(None)
    assert result == []


def test_classify_stock_feed_with_tickers():
    assert classify_item([{"ticker": "AAPL", "confidence": 100}], "stock_specific") == "stock_specific"


def test_extract_ticker_in_parentheses():
    result = extract_tickers_from_text("Stock (MSFT) announced earnings")
    tickers = [t["ticker"] for t in result]
    assert "MSFT" in tickers


def test_extract_ticker_at_start():
    result = extract_tickers_from_text("AAPL reported record revenue")
    tickers = [t["ticker"] for t in result]
    assert "AAPL" in tickers


def test_extract_multiple_companies():
    result = extract_tickers_from_text("Google and Amazon both reported strong quarters")
    tickers = [t["ticker"] for t in result]
    assert "GOOGL" in tickers
    assert "AMZN" in tickers


def test_extract_confidence_exact_ticker():
    result = extract_tickers_from_text("AAPL is up 5%")
    for t in result:
        if t["ticker"] == "AAPL":
            assert t["confidence"] == 100


def test_extract_confidence_company_name():
    result = extract_tickers_from_text("Apple Inc. reported earnings")
    for t in result:
        if t["ticker"] == "AAPL":
            assert t["confidence"] == 90


def test_classify_empty_tickers_market_feed():
    assert classify_item([], "market_wide") == "market_wide"


def test_classify_single_ticker_market_feed():
    assert classify_item([{"ticker": "AAPL", "confidence": 100}], "market_wide") == "market_wide"


def test_classify_multiple_tickers_market_feed():
    result = classify_item(
        [{"ticker": "AAPL", "confidence": 100}, {"ticker": "MSFT", "confidence": 90}],
        "market_wide"
    )
    assert result == "stock_specific"


def test_extract_ticker_case_insensitive():
    result = extract_tickers_from_text("aapl reported earnings")
    tickers = [t["ticker"] for t in result]
    assert "AAPL" in tickers
