from typing import Optional
from app.schemas.market import MarketItemCreate, MarketItemResponse

# In-memory store (stub — replace with DB calls when ready)
_store: dict[int, dict] = {}
_counter: int = 0


class MarketRepository:
    def get_all(self) -> list[MarketItemResponse]:
        return [MarketItemResponse(id=k, **v) for k, v in _store.items()]

    def get_by_id(self, item_id: int) -> Optional[MarketItemResponse]:
        item = _store.get(item_id)
        if item is None:
            return None
        return MarketItemResponse(id=item_id, **item)

    def create(self, payload: MarketItemCreate) -> MarketItemResponse:
        global _counter
        _counter += 1
        _store[_counter] = payload.model_dump()
        return MarketItemResponse(id=_counter, **payload.model_dump())

    def delete(self, item_id: int) -> bool:
        if item_id not in _store:
            return False
        del _store[item_id]
        return True
