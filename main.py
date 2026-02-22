from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
from pathlib import Path
import uuid

DATA_FILE = Path("items.json")

# Load existing items
if DATA_FILE.exists():
    with open(DATA_FILE) as file:
        items = json.load(file)  # Now this will be a dict {user_id: [items]}
else:
    items = {}

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Item Model
class Item(BaseModel):
    ToDo: str

# Helper to save to file
def save_items():
    with open(DATA_FILE, "w") as file:
        json.dump(items, file)

# Index Page
@app.get("/index", response_class=HTMLResponse)
def home(request: Request, response: Response):
    # Get or create user_id cookie
    user_id = request.cookies.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        response.set_cookie(key="user_id", value=user_id)
    
    user_items = items.get(user_id, [])
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "items": user_items
        }
    )

# Add item
@app.post("/item")
def create_item(item: Item, request: Request, response: Response):
    user_id = request.cookies.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        response.set_cookie(key="user_id", value=user_id)
    
    user_items = items.setdefault(user_id, [])
    user_items.append(item.dict())
    
    save_items()
    return {"success": True, "item": item.dict()}

# List items for this user
@app.get("/items")
def list_items(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id or user_id not in items:
        return []
    return items[user_id]

# Get a single item for this user
@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int, request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id or user_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    user_items = items[user_id]
    if item_id < len(user_items):
        return user_items[item_id]
    raise HTTPException(status_code=404, detail=f"Item {item_id} was not found")