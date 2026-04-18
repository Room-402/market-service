from pydantic import BaseModel


class MarketItemBase(BaseModel):
    name: str
    price: float
    quantity: int


class MarketItemCreate(MarketItemBase):
    pass


class MarketItemResponse(MarketItemBase):
    id: int

    class Config:
        from_attributes = True
