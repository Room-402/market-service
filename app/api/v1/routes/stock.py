from fastapi import APIRouter, Depends, Query
from app.services.stock_service import StockService
from app.schemas.stock import NiftyResponse
from typing import List, Optional

router = APIRouter(prefix="/stocks", tags=["Stocks"])

def get_stock_service() -> StockService:
    return StockService()

@router.get("/nifty50", response_model=NiftyResponse)
async def fetch_nifty_data(service: StockService = Depends(get_stock_service)):
    data = await service.get_nifty_50_data()
    return {"stocks": data}

@router.get("/get_stock_details")
def get_stock_details(
    symbol: str, 
    ttl: Optional[int] = Query(None, description="Custom TTL in seconds"),
    service: StockService = Depends(get_stock_service)
):
    data = service.get_stock_details(symbol, ttl)
    return {"stock_details": data}

@router.get("/get_stock_details_batch")
def get_stock_details_batch(
    symbols: List[str] = Query(...),
    ttl: Optional[int] = Query(None, description="Custom TTL in seconds"),
    service: StockService = Depends(get_stock_service)
):
    data = service.get_stock_details_batch(symbols, ttl) 
    return {"stock_details": data}