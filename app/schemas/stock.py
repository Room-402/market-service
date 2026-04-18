from pydantic import BaseModel
from typing import List, Optional

class StockData(BaseModel):
    symbol: str
    price: Optional[float] = None
    change: Optional[float] = None
    company_name: str
    
    
class NiftyResponse(BaseModel):
    stocks: List[StockData]
    
    
class Stock(BaseModel):
    symbol: str
    company_name: str
    industry: str
    series: str
    isin_code: str