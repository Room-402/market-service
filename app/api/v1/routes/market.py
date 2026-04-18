from fastapi import APIRouter
from app.schemas.market import MarketItemCreate, MarketItemResponse
from app.services.market_service import MarketService

router = APIRouter(prefix="/markets", tags=["Markets"])

_service = MarketService()


@router.get("/", response_model=list[MarketItemResponse])
def list_items():
    """List all market items."""
    return _service.list_items()


@router.get("/{item_id}", response_model=MarketItemResponse)
def get_item(item_id: int):
    """Get a single market item by ID."""
    return _service.get_item(item_id)


@router.post("/", response_model=MarketItemResponse, status_code=201)
def create_item(payload: MarketItemCreate):
    """Create a new market item."""
    return _service.create_item(payload)


@router.delete("/{item_id}")
def delete_item(item_id: int):
    """Delete a market item by ID."""
    return _service.delete_item(item_id)
