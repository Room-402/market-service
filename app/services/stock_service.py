import yfinance as yf
import math
import json
import requests
import logging
from typing import List, Optional, Callable, Any
from app.repositories.stock_repository import StockRepository
from app.core.redis_client import get_redis
from app.core.config import settings
from app.schemas.stock import StockSearchResponse

logger = logging.getLogger(__name__)

class StockService:
    def __init__(self, repository: StockRepository = None):
        self.repository = repository or StockRepository()
        self.redis = get_redis()
        # Use a custom session to bypass Yahoo Finance rate limits
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def _get_cached_or_fetch(self, cache_key: str, fetch_fn: Callable, ttl: int) -> Any:
        """
        Generic Cache-Aside helper.
        """
        try:
            cached = self.redis.get(cache_key)
            if cached:
                logger.info(f"Cache HIT for key: {cache_key}")
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Redis error during GET for {cache_key}: {e}")

        logger.info(f"Cache MISS for key: {cache_key}. Fetching fresh data...")
        fresh_data = fetch_fn()
        
        try:
            self.redis.setex(cache_key, ttl, json.dumps(fresh_data))
        except Exception as e:
            logger.error(f"Redis error during SET for {cache_key}: {e}")
            
        return fresh_data

    async def get_nifty_50_data(self, ttl: int = settings.NIFTY50_TTL):
        cache_key = "nifty_50_live_data"
        
        async def fetch_nifty():
            stocks = await self.repository.get_nifty_50_stocks()
            tickers = [f"{s.symbol}.NS" for s in stocks]

            data = yf.download(
                tickers=tickers, 
                period="1d", 
                group_by='ticker', 
                threads=True,
                progress=False,
                session=self.session
            )
            
            results = []
            for stock in stocks:
                ticker = f"{stock.symbol}.NS"
                try:
                    if ticker not in data.columns.levels[0]:
                        continue

                    raw_close = data[ticker]['Close'].iloc[-1]
                    raw_open = data[ticker]['Open'].iloc[-1]
                    
                    price = None if math.isnan(raw_close) else round(float(raw_close), 2)
                    change = None
                    if not math.isnan(raw_close) and not math.isnan(raw_open):
                        change = round(float(raw_close - raw_open), 2)
                    results.append({
                        "symbol": stock.symbol,
                        "company_name": stock.company_name,
                        "price": price,
                        "change": change
                    })
                except Exception:
                    continue
            return results

        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass

        fresh_data = await fetch_nifty()
        
        try:
            self.redis.setex(cache_key, ttl, json.dumps(fresh_data))
        except Exception:
            pass
            
        return fresh_data
    
    def get_stock_details(self, symbol: str, ttl: Optional[int] = None):
        symbol = symbol.upper()
        cache_key = f"stock:{symbol}:details"
        target_ttl = ttl if ttl is not None else settings.PRICE_TTL

        def fetch_details():
            ticker_symbol = f"{symbol}"
            ticker = yf.Ticker(ticker_symbol, session=self.session)
            data = ticker.info

            return {
                "symbol": symbol,
                "price": data.get("currentPrice"),
                "day_high": data.get("dayHigh"),
                "day_low": data.get("dayLow"),
                "company_name": data.get("longName"),
                "pe_ratio": data.get("forwardPE"),
                "market_cap": data.get("marketCap"),
                "other_details": data
            }
        return self._get_cached_or_fetch(cache_key, fetch_details, target_ttl)
    
    def get_stock_details_batch(self, symbols: List[str], ttl: Optional[int] = None):
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_stock_details(symbol, ttl)
        return results

    def search_stocks(self, query: str, ttl: Optional[int] = None):
        cache_key = f"search:{query}"
        target_ttl = ttl if ttl is not None else settings.SEARCH_TTL

        def fetch_search():
            search = yf.Search(query, max_results=15, enable_fuzzy_query=True, session=self.session)
            equities = [q for q in search.quotes if q.get("quoteType") == "EQUITY" and (q.get("exchange") in ["NSI", "NSE", "BSE"])]
            return [
                {
                    "ticker": q.get("symbol", ""),
                    "company_name": q.get("shortname", ""),
                    "exchange": q.get("exchange", "")
                }
                for q in equities
            ]

        return self._get_cached_or_fetch(cache_key, fetch_search, target_ttl)

    def get_stock_history(self, symbol: str, period: str, interval: str, ttl: Optional[int] = None):
        symbol = symbol.upper()
        cache_key = f"stock:{symbol}:history:{period}:{interval}"
        target_ttl = ttl if ttl is not None else 3600

        def fetch_history():
            ticker_symbol = f"{symbol}"
            ticker = yf.Ticker(ticker_symbol, session=self.session)
            hist = ticker.history(period=period, interval=interval)
            
            results = []
            for date, row in hist.iterrows():
                results.append({
                    "timestamp": str(date),
                    "price": round(float(row["Close"]), 2)
                })
            return results

        return self._get_cached_or_fetch(cache_key, fetch_history, target_ttl)
