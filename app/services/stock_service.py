from yahooquery import Ticker
import math
import json
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

    def _get_cached_or_fetch(self, cache_key: str, fetch_fn: Callable, ttl: int) -> Any:
        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Redis error: {e}")

        fresh_data = fetch_fn()
        
        try:
            self.redis.setex(cache_key, ttl, json.dumps(fresh_data))
        except Exception as e:
            logger.error(f"Redis error: {e}")
            
        return fresh_data

    async def get_nifty_50_data(self, ttl: int = settings.NIFTY50_TTL):
        cache_key = "nifty_50_live_data"
        
        async def fetch_nifty():
            stocks = await self.repository.get_nifty_50_stocks()
            tickers_list = [f"{s.symbol}.NS" for s in stocks]
            
            # yahooquery handles batch requests very efficiently
            t = Ticker(tickers_list, asynchronous=True)
            prices = t.price
            
            results = []
            for stock in stocks:
                symbol_ns = f"{stock.symbol}.NS"
                try:
                    detail = prices.get(symbol_ns, {})
                    if isinstance(detail, str): # Error message
                        continue
                        
                    price = detail.get("regularMarketPrice")
                    change = detail.get("regularMarketChange")
                    
                    results.append({
                        "symbol": stock.symbol,
                        "company_name": stock.company_name,
                        "price": price,
                        "change": change
                    })
                except Exception:
                    continue
            return results

        return self._get_cached_or_fetch(cache_key, fetch_nifty, ttl)
    
    def get_stock_details(self, symbol: str, ttl: Optional[int] = None):
        symbol = symbol.upper()
        ticker_symbol = symbol if "." in symbol else f"{symbol}.NS"
        cache_key = f"stock:{ticker_symbol}:details"
        target_ttl = ttl if ttl is not None else settings.PRICE_TTL

        def fetch_details():
            t = Ticker(ticker_symbol)
            # summary_detail and price contain almost everything
            all_modules = t.all_modules.get(ticker_symbol, {})
            
            if isinstance(all_modules, str):
                logger.error(f"YahooQuery error for {ticker_symbol}: {all_modules}")
                return None

            price_data = all_modules.get("price", {})
            summary_data = all_modules.get("summaryDetail", {})
            
            return {
                "symbol": ticker_symbol,
                "price": price_data.get("regularMarketPrice"),
                "day_high": price_data.get("regularMarketDayHigh"),
                "day_low": price_data.get("regularMarketDayLow"),
                "company_name": price_data.get("longName"),
                "pe_ratio": summary_data.get("forwardPE"),
                "market_cap": price_data.get("marketCap"),
                "other_details": all_modules
            }
        return self._get_cached_or_fetch(cache_key, fetch_details, target_ttl)
    
    def get_stock_details_batch(self, symbols: List[str], ttl: Optional[int] = None):
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_stock_details(symbol, ttl)
        return results

    def search_stocks(self, query: str, ttl: Optional[int] = None):
        # Search still uses the standard Scraper, but yahooquery's implementation is often cleaner
        cache_key = f"search:{query}"
        target_ttl = ttl if ttl is not None else settings.SEARCH_TTL

        def fetch_search():
            # For searching, we still use yfinance or another logic if yahooquery search is limited
            # But let's try yahooquery's built-in search if possible or just stick to a logic that works
            import requests
            url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = resp.json()
            
            quotes = data.get("quotes", [])
            return [
                {
                    "ticker": q.get("symbol", ""),
                    "company_name": q.get("shortname", ""),
                    "exchange": q.get("exchange", "")
                }
                for q in quotes if q.get("quoteType") == "EQUITY"
            ]

        return self._get_cached_or_fetch(cache_key, fetch_search, target_ttl)

    def get_stock_history(self, symbol: str, period: str, interval: str, ttl: Optional[int] = None):
        symbol = symbol.upper()
        ticker_symbol = symbol if "." in symbol else f"{symbol}.NS"
        cache_key = f"stock:{ticker_symbol}:history:{period}:{interval}"
        target_ttl = ttl if ttl is not None else 3600

        def fetch_history():
            t = Ticker(ticker_symbol)
            df = t.history(period=period, interval=interval)
            
            results = []
            if df.empty:
                return results
                
            # yahooquery history returns a DataFrame with MultiIndex (symbol, date)
            for index, row in df.iterrows():
                results.append({
                    "timestamp": str(index[1]) if isinstance(index, tuple) else str(index),
                    "price": round(float(row["close"]), 2)
                })
            return results

        return self._get_cached_or_fetch(cache_key, fetch_history, target_ttl)
