from pydantic import BaseModel

class ItemPriceSchema(BaseModel):
    id: int
    catagory_id: int
    product_id: int
    normal_price: float
    title: str
    discount: float
    out_of_stock: int

    class Config:
        from_attributes = True