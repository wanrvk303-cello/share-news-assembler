import logging
import re
from difflib import SequenceMatcher
from app.tickers import COMMON_TICKERS

logger = logging.getLogger(__name__)

SHORT_NAMES = {
    "APPLE": "AAPL",
    "MICROSOFT": "MSFT",
    "GOOGLE": "GOOGL",
    "ALPHABET": "GOOGL",
    "AMAZON": "AMZN",
    "META": "META",
    "FACEBOOK": "META",
    "TESLA": "TSLA",
    "NVIDIA": "NVDA",
    "JPMORGAN": "JPM",
    "CHASE": "JPM",
    "VISA": "V",
    "JOHNSON": "JNJ",
    "WALMART": "WMT",
    "PROCTER": "PG",
    "GAMBLE": "PG",
    "MASTERCARD": "MA",
    "UNITEDHEALTH": "UNH",
    "HOME DEPOT": "HD",
    "DISNEY": "DIS",
    "BANK OF AMERICA": "BAC",
    "EXXON": "XOM",
    "MOBIL": "XOM",
    "CISCO": "CSCO",
    "NETFLIX": "NFLX",
    "INTEL": "INTC",
    "SALESFORCE": "CRM",
    "PFIZER": "PFE",
    "ABBOTT": "ABT",
    "COCA COLA": "KO",
    "COKE": "KO",
    "PEPSI": "PEP",
    "PEPSICO": "PEP",
    "NIKE": "NKE",
    "MERCK": "MRK",
    "VERIZON": "VZ",
    "ADOBE": "ADBE",
    "PAYPAL": "PYPL",
    "COMCAST": "CMCSA",
    "ACCENTURE": "ACN",
    "BROADCOM": "AVGO",
    "TEXAS INSTRUMENTS": "TXN",
    "QUALCOMM": "QCOM",
    "COSTCO": "COST",
    "AMD": "AMD",
    "ADVANCED MICRO": "AMD",
    "GILEAD": "GILD",
    "THERMO FISHER": "TMO",
    "MCDONALD": "MCD",
    "CONOCOPHILLIPS": "COP",
    "WELLS FARGO": "WFC",
    "BRISTOL": "BMY",
    "MYERS": "BMY",
    "SQUIBB": "BMY",
    "NEXTERA": "NEE",
    "PHILIP MORRIS": "PM",
    "UPS": "UPS",
    "HONEYWELL": "HON",
    "LOWE": "LOW",
    "ORACLE": "ORCL",
    "STARBUCKS": "SBUX",
    "IBM": "IBM",
    "BOEING": "BA",
    "GOLDMAN": "GS",
    "SACHS": "GS",
    "CATERPILLAR": "CAT",
    "MONDELEZ": "MDLZ",
    "DEERE": "DE",
    "BLACKROCK": "BLK",
    "AMERICAN EXPRESS": "AXP",
    "STRYKER": "SYK",
    "INTUITIVE SURGICAL": "ISRG",
    "PROLOGIS": "PLD",
    "ANALOG DEVICES": "ADI",
    "MARSH": "MMC",
    "MCLENNAN": "MMC",
    "CME GROUP": "CME",
    "CHARLES SCHWAB": "SCHW",
    "SCHWAB": "SCHW",
    "CHUBB": "CB",
    "SOUTHERN COMPANY": "SO",
    "CIGNA": "CI",
    "DUKE ENERGY": "DUK",
    "PROGRESSIVE": "PGR",
    "COLGATE": "CL",
    "FEDEX": "FDX",
    "TARGET": "TGT",
    "EOG RESOURCES": "EOG",
    "NORFOLK SOUTHERN": "NSC",
    "PNC": "PNC",
    "TRUIST": "TFC",
    "REGENERON": "REGN",
    "SCHLUMBERGER": "SLB",
    "WASTE MANAGEMENT": "WM",
    "BECTON": "BDX",
    "DICKINSON": "BDX",
    "INTERCONTINENTAL": "ICE",
    "SHERWIN": "SHW",
    "WILLIAMS": "SHW",
    "MCKESSON": "MCK",
    "ZOETIS": "ZTS",
    "NORTHROP": "NOC",
    "GRUMMAN": "NOC",
    "GENERAL DYNAMICS": "GD",
    "EMERSON": "EMR",
    "FORD": "F",
    "GENERAL MOTORS": "GM",
    "TAIWAN SEMI": "TSM",
    "TSMC": "TSM",
    "SONY": "SONY",
    "NIO": "NIO",
    "SNAP": "SNAP",
    "SNAPCHAT": "SNAP",
    "UBER": "UBER",
    "AIRBNB": "ABNB",
    "COINBASE": "COIN",
    "BLOCK": "SQ",
    "SQUARE": "SQ",
    "RIVIAN": "RIVN",
    "PALANTIR": "PLTR",
    "SOFI": "SOFI",
    "DRAFTKINGS": "DKNG",
    "ROKU": "ROKU",
    "SHOPIFY": "SHOP",
    "SPOTIFY": "SPOT",
    "SNOWFLAKE": "SNOW",
    "CLOUDFLARE": "NET",
    "CROWDSTRIKE": "CRWD",
    "DATADOG": "DDOG",
    "MONGODB": "MDB",
    "ZSCALER": "ZS",
    "PALO ALTO": "PANW",
}


def extract_tickers_from_text(text: str) -> list[dict]:
    """Extract stock tickers from text using keyword matching."""
    if not text:
        return []

    text_upper = text.upper()
    found = []

    for ticker, name in COMMON_TICKERS.items():
        ticker_pattern = r'\b' + re.escape(ticker) + r'\b'
        if re.search(ticker_pattern, text_upper):
            if not any(f["ticker"] == ticker for f in found):
                found.append({"ticker": ticker, "confidence": 100})

    for short_name, ticker in SHORT_NAMES.items():
        if short_name in text_upper:
            if not any(f["ticker"] == ticker for f in found):
                found.append({"ticker": ticker, "confidence": 85})

    for ticker, name in COMMON_TICKERS.items():
        name_upper = name.upper()
        if name_upper in text_upper:
            if not any(f["ticker"] == ticker for f in found):
                found.append({"ticker": ticker, "confidence": 90})

    if found:
        logger.debug(f"Extracted tickers: {[t['ticker'] for t in found]}")
    return found


def classify_item(tickers_found: list[dict], feed_type: str) -> str:
    """Classify news item as 'market_wide' or 'stock_specific'."""
    if feed_type == "market_wide" and len(tickers_found) <= 1:
        return "market_wide"
    return "stock_specific"
