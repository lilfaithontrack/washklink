from sqlalchemy import Column, Integer, Float, String
from app.core.database import Base

class ItemPrice(Base):
    __tablename__ = "tbl_item_price_with_catagory"

    id = Column(Integer, primary_key=True, index=True)
    catagory_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    normal_price = Column(Float, nullable=False)
    title = Column(String, nullable=False)
    discount = Column(Float, nullable=False)
    out_of_stock = Column(Integer, nullable=False)