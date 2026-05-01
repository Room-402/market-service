import yfinance as yf
import json
import logging
from typing import Optional, Any, Callable
from app.core.redis_client import get_redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class MarketService:
    def __init__(self):
        self.redis = get_redis()

    def _get_cached_or_fetch(self, cache_key: str, fetch_fn: Callable, ttl: int) -> Any:
        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass

        fresh_data = fetch_fn()
        
        try:
            self.redis.setex(cache_key, ttl, json.dumps(fresh_data))
        except Exception:
            pass
            
        return fresh_data

    def get_market_indices(self, ttl: int = settings.INDICES_TTL):
        cache_key = "market_indices"

        def fetch_indices():
            indices = ["^NSEI", "^BSESN"]
            results = {}
            for index in indices:
                ticker = yf.Ticker(index)
                data = ticker.info
                name = "Nifty 50" if index == "^NSEI" else "Sensex"
                
                results[name] = {
                    "price": data.get("regularMarketPrice") or data.get("currentPrice"),
                    "change_percent": data.get("regularMarketChangePercent")
                }
            return results

        return self._get_cached_or_fetch(cache_key, fetch_indices, ttl)
