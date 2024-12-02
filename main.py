import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine, select, delete
from sqlalchemy.orm import sessionmaker
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base = declarative_base()

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://admin:admin@postgresDb/shoppingDb"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL,echo = True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Item(Base):
    __tablename__ = "items"
    __allow_unmapped__ = True  # Add this line
    
    name = Column(String, primary_key=True)
    amount = Column(Integer)

    def serialize(self):
        return {"name": self.name, "amount": self.amount}
    
class ItemSchema(BaseModel):
    name: str
    amount: int

class ItemResponse(ItemSchema):
    id: int

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

#@app.on_event("startup")
#async def startup_event():
#    await init_db()

@app.post("/api/shopping", response_model=ItemResponse)
async def create_item(item: ItemSchema, db: AsyncSession = Depends(get_db)):
    db_item = Item(name=item.name, amount=item.amount)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

@app.get("/api/shopping", response_model=List[ItemResponse])
async def get_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    items = result.scalars().all()
    return items

@app.get("/api/shopping/{item_name}", response_model=ItemResponse)
async def get_item(item_name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).filter(Item.name == item_name))
    item = result.scalars().first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/api/shopping/{item_name}", response_model=ItemResponse)
async def update_item(item_name: str, item: ItemSchema, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).filter(Item.name == item_name))
    existing_item = result.scalars().first()
    if existing_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    existing_item.name = item.name
    existing_item.amount = item.amount
    
    await db.commit()
    await db.refresh(existing_item)
    return existing_item

@app.delete("/api/shopping/{item_name}")
async def delete_item(item_name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).filter(Item.name == item_name))
    item = result.scalars().first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await db.execute(delete(Item).where(Item.name == item_name))
    await db.commit()
    return {"message": "Item deleted successfully"}

# Add custom route for Swagger UI
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    return get_swagger_ui_html(
        app.openapi_url,
        title="Custom Swagger UI"
    )

#test route
@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
