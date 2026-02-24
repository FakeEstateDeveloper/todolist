from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import ItemDB, User, Base
from database import engine, SessionLocal

# Create tables
Base.metadata.create_all(bind=engine)

# Create the web server
app = FastAPI()

# Let the web server access the java and css files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Let the ...
templates = Jinja2Templates(directory="templates")


# ---------- DB session ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Pydantic model ----------
class Item(BaseModel):
    ToDo: str


# ---------- USER HELPER ----------
def get_or_create_user(request: Request, response: Response, db: Session):
    cookie_user_id = request.cookies.get("user_id")

    # If cookie exists, verify user in DB
    if cookie_user_id:
        user = db.query(User).filter(User.id == int(cookie_user_id)).first()
        if user:
            return user

    # Otherwise create a new user
    new_user = User()
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    response.set_cookie(key="user_id", value=str(new_user.id))
    return new_user


# ---------- INDEX PAGE ----------
@app.get("/index", response_class=HTMLResponse)
def home(request: Request, response: Response, db: Session = Depends(get_db)):
    user = get_or_create_user(request, response, db)

    # Filter makes it so each user can only see their own items
    items = db.query(ItemDB).filter(ItemDB.user_id == user.id).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "items": items
        }
    )


# ---------- CREATE ITEM ----------
@app.post("/item")
def create_item(item: Item, request: Request, response: Response, db: Session = Depends(get_db)):
    user = get_or_create_user(request, response, db)

    db_item = ItemDB(user_id=user.id, todo=item.ToDo)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return {"success": True, "item": {"id": db_item.id, "ToDo": db_item.todo}}


# ---------- LIST ITEMS ----------
@app.get("/items")
def list_items(request: Request, response: Response, db: Session = Depends(get_db)):
    user = get_or_create_user(request, response, db)

    items = db.query(ItemDB).filter(ItemDB.user_id == user.id).all()
    return [{"id": i.id, "ToDo": i.todo} for i in items]


# ---------- GET ONE ITEM ----------
@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int, request: Request, response: Response, db: Session = Depends(get_db)):
    user = get_or_create_user(request, response, db)

    item = (
        db.query(ItemDB)
        .filter(ItemDB.user_id == user.id, ItemDB.id == item_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"ToDo": item.todo}