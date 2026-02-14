from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    text: str # No default means required
    is_done: bool = False

items = []

# Shows items list
@app.get("/")
def root():
    return {"Items": items}

# Add item to list
@app.post("/item")
def create_item(item: Item):
    items.append(item)
    return items

# Shows all items up to limit
@app.get("/items", response_model=list[Item])
def list_items(limit: int=10):
    return items[0:limit]

# Get item from list
@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    if item_id < len(items):
        return items[item_id]
    raise HTTPException(status_code=404, detail=f"Item {item_id} was not found")

# ACTIVATE
# ====
# ACTIVATE test API Command:
# python -m uvicorn main:app --reload

# RUN
# ====
# RUN the web so that others can access it:
# source venv/bin/activate  # activate virtual environment
# uvicorn main:app --reload --host 0.0.0.0 --port 8000

# POST
# ====
# POST 'apple' item to list:
# Invoke-RestMethod -Uri "http://127.0.0.1:8000/item?item=apple" -Method POST

# GET
# ====
# GET index up to limit item from the list:
# Invoke-RestMethod -Uri "http://127.0.0.1:8000/items?limit=3"

# GET index '0''s item from the list:
# Invoke-RestMethod -Uri "http://127.0.0.1:8000/items/0"