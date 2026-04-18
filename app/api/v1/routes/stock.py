from fastapi import APIRouter, Depends
from app.services.stock_service import StockService
from app.schemas.stock import NiftyResponse

router = APIRouter(prefix="/stocks", tags=["Stocks"])

def get_stock_service() -> StockService:
    # Factory function bypasses FastAPI constructor introspection
    return StockService()

@router.get("/nifty50", response_model=NiftyResponse)
async def fetch_nifty_data(service: StockService = Depends(get_stock_service)):
    data = await service.get_nifty_50_data()
    return {"stocks": data}
    
@router.get("/{symbol}", response_model=StockData)
async def get_stock_by_symbol(
    symbol: str, 
    exchange: str = Query(default="NSE", description="The stock exchange (NSE or BSE)"),
    service: StockService = Depends(get_stock_service)):
    data = await service.get_stock_data(symbol, exchange)
    return {"data": data}
    
      
      
    

  

  