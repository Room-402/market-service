from fastapi import APIRouter, Depends, Query
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

@router.get("/get_stock_details")
def get_stock_details(symbol: str,service: StockService = Depends(get_stock_service) ):
    data = service.get_stock_details(symbol)
    return {"stock_details": data}

@router.get("/get_stock_details_batch")
def get_stock_details_batch(symbols: list[str] = Query(...),
    service: StockService = Depends(get_stock_service)):
    data = service.get_stock_details_batch(symbols) 
    return {"stock_details": data}
    
@router.get("/search")
def search(query: str,service: StockService = Depends(get_stock_service) ):
    data = service.search_stocks(query)
    return {"items": data}
    
    
    
      
      
    

  

  