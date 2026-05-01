import yfinance as yf
from typing import Optional
from fastapi import HTTPException, status
from app.schemas.market import MarketItemCreate, MarketItemResponse
from app.repositories.market_repository import MarketRepository


class MarketService:
    def __init__(self, repository: MarketRepository = None):
        self.repository = repository or MarketRepository()
    
    def get_market_indices(self):
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
