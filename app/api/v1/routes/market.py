from fastapi import APIRouter, Depends
from app.schemas.market import MarketItemCreate, MarketItemResponse
from app.services.market_service import MarketService

router = APIRouter(prefix="/markets", tags=["Markets"])


def get_market_service() -> MarketService:
    # Factory function bypasses FastAPI constructor introspection
    return MarketService()


@router.get("/get_market_indices")
def get_market_indices(service: MarketService = Depends(get_market_service)):
    data = service.get_market_indices()
    return data
    
