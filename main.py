from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Item(BaseModel):
    text: str                   # No default means required
    is_done: bool = False

items = []

# Index Page
@app.get("/index", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "items": items      # Sends items to html
        }
    )

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