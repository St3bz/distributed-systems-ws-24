#from fastapi import FastAPI

#app = FastAPI()


#@app.get("/")
#async def root():
#    return {"message": "Hello World"}

import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import logging



logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base = declarative_base()

SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://admin:admin@db/shoppingDB")
#engine = create_engine(SQLALCHEMY_DATABASE_URL)
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

class Item(Base):
    __tablename__ = "items"
    name = Column(String, primary_key=True)
    amount = Column(Integer)

    def serialize(self):
        return {"name": self.name, "amount": self.amount}

class ItemSchema(BaseModel):
    name: str
    amount: int

class ItemResponse(ItemSchema):
    id: int

async def init_db():
        Base.metadata.create_all(bind=engine)

@app.post("/api/shopping", response_model=ItemResponse)
async def create_item(item: ItemSchema, db: AsyncSession = Depends(get_db)):
    db_item = Item(name=item.name, amount=item.amount)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/api/shopping", response_model=List[ItemResponse])
async def get_items(db: AsyncSession = Depends(get_db)):
    items = db.query(Item).all()
    return items

@app.get("/api/shopping/{item_name}", response_model=ItemResponse)
async def get_item(item_name: str, db: AsyncSession = Depends(get_db)):
    item = db.query(Item).filter(Item.name == item_name).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/api/shopping/{item_name}", response_model=ItemResponse)
async def update_item(item_name: str, item: ItemSchema, db: AsyncSession = Depends(get_db)):
    existing_item = db.query(Item).filter(Item.name == item_name).first()
    if existing_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    existing_item.name = item.name
    existing_item.amount = item.amount
    
    db.commit()
    db.refresh(existing_item)
    return existing_item

@app.delete("/api/shopping/{item_name}")
async def delete_item(item_name: str, db: AsyncSession = Depends(get_db)):
    item = db.query(Item).filter(Item.name == item_name).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}

# Add custom route for Swagger UI
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    return get_swagger_ui_html(
        app,
        title=f"{app.title} - Swagger UI",
        openapi_url=f"{app.prefix}/openapi.json",
        swagger_js_url=f"{app.prefix}/swagger-ui-bundle.js",
        swagger_css_url=f"{app.prefix}/swagger-ui.css",
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
