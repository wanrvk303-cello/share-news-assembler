import logging
import re
from difflib import SequenceMatcher
from app.tickers import COMMON_TICKERS

logger = logging.getLogger(__name__)


def extract_tickers_from_text(text: str) -> list[dict]:
    """Extract stock tickers from text using keyword matching.

    Returns list of dicts with 'ticker' and 'confidence' keys.
    """
    if not text:
        return []

    text_upper = text.upper()
    found = []

    for ticker, name in COMMON_TICKERS.items():
        ticker_pattern = r'\b' + re.escape(ticker) + r'\b'
        if re.search(ticker_pattern, text_upper):
            found.append({"ticker": ticker, "confidence": 100})

        name_upper = name.upper()
        if name_upper in text_upper or _fuzzy_name_match(text_upper, name_upper):
            if not any(f["ticker"] == ticker for f in found):
                conf = 90 if name_upper in text_upper else 70
                found.append({"ticker": ticker, "confidence": conf})

    if found:
        logger.debug(f"Extracted tickers: {[t['ticker'] for t in found]}")
    return found


def _fuzzy_name_match(text: str, name: str, threshold: float = 0.85) -> bool:
    words = text.split()
    name_words = name.split()
    if len(name_words) < 2:
        return False

    for i in range(len(words) - len(name_words) + 1):
        candidate = " ".join(words[i : i + len(name_words)])
        ratio = SequenceMatcher(None, candidate, name).ratio()
        if ratio >= threshold:
            return True
    return False


def classify_item(tickers_found: list[dict], feed_type: str) -> str:
    """Classify news item as 'market_wide' or 'stock_specific'."""
    if feed_type == "market_wide" and len(tickers_found) <= 1:
        return "market_wide"
    return "stock_specific"
