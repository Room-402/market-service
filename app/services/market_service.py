from typing import Optional
from fastapi import HTTPException, status
from app.schemas.market import MarketItemCreate, MarketItemResponse
from app.repositories.market_repository import MarketRepository


class MarketService:
    def __init__(self, repository: MarketRepository = None):
        self.repository = repository or MarketRepository()

    def list_items(self) -> list[MarketItemResponse]:
        return self.repository.get_all()

    def get_item(self, item_id: int) -> MarketItemResponse:
        item = self.repository.get_by_id(item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found.",
            )
        return item

    def create_item(self, payload: MarketItemCreate) -> MarketItemResponse:
        return self.repository.create(payload)

    def delete_item(self, item_id: int) -> dict:
        deleted = self.repository.delete(item_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with id {item_id} not found.",
            )
        return {"message": f"Item {item_id} deleted successfully."}
