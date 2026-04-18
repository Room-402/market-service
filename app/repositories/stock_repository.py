import csv
import httpx
from io import StringIO
from typing import List
from app.schemas.stock import Stock

class StockRepository:
    NSE_NIFTY_50_URL = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
    
    def __init__(self):
        # NSE requires a real browser headers to allow requests
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

    async def get_nifty_50_stocks(self) -> List[Stock]:
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(self.NSE_NIFTY_50_URL)
            response.raise_for_status()
            
            f = StringIO(response.text)
            reader = csv.DictReader(f)
            
            stocks = []
            for row in reader:
                stocks.append(Stock(
                    symbol=row["Symbol"],
                    company_name=row["Company Name"],
                    industry=row["Industry"],
                    series=row["Series"],
                    isin_code=row["ISIN Code"]
                ))
            return stocks
