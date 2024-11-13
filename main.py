from fastapi import FastAPI

app = FastAPI(__name__)

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id, "name": "Item name", "price": 100}
