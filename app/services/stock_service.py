import yfinance as yf
import math
from cachetools import TTLCache
from app.repositories.stock_repository import StockRepository

# Cache for 10 minutes, max 1 item (the whole list)
_cache = TTLCache(maxsize=1, ttl=600)
_CACHE_KEY = "nifty_50_live_data"

class StockService:
    def __init__(self, repository: StockRepository = None):
        self.repository = repository or StockRepository()

    async def get_nifty_50_data(self):
        # 1. Check cache first
        #if _CACHE_KEY in _cache:
        #    return _cache[_CACHE_KEY]

        # 2. Get dynamic tickers from Repository (NSE CSV)
        stocks = await self.repository.get_nifty_50_stocks()
        # Convert NSE symbols to Yahoo Finance tickers (add .NS)
        tickers = [f"{s.symbol}.NS" for s in stocks]

        # 3. Fetch live prices from Yahoo Finance
        data = yf.download(
            tickers=tickers, 
            period="1d", 
            group_by='ticker', 
            threads=True,
            progress=False
        )
        
        results = []
        for stock in stocks:
            ticker = f"{stock.symbol}.NS"
            try:
                # Basic check to see if ticker is in the download result
                if ticker not in data.columns.levels[0]:
                    continue

                raw_close = data[ticker]['Close'].iloc[-1]
                raw_open = data[ticker]['Open'].iloc[-1]
                
                # Handle NaN for JSON safety
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
        
        # 4. Save to cache
        _cache[_CACHE_KEY] = results
        return results
        
        
        