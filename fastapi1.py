from fastapi import FastAPI, Query
from typing import List, Optional
app = FastAPI()

# Simple root endpoint (we already had this)
@app.get("/")
def read_root():
    return {"message": "Hello World from Mohamed! 🚀 Cairo 2026"}

# New: Path parameter example
# The {name} part becomes a variable we can use
@app.get("/hello/{name}")
def say_hello(name: str):
    return {"greeting": f"Hello, {name}! Welcome to FastAPI 🌟"}

# Another path parameter example - with type (int)
@app.get("/items1/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "description": "This is item number " + str(item_id)}

# Bonus: What happens if someone sends wrong type?
# Try /items/abc in browser → FastAPI gives nice error automatically!

# ------------------------------------------------------------------------------------------------------------------

#Add Query Parameters

# http://127.00.1:8000/search/?q=fastapi&skip=5&limit=10
@app.get("/search/")
def search_items(q: str = None,skip: int = 0, limit: int = 10):
    result= {"query": q, "skip": skip, "limit": limit}
    if q:
        result["results"] = [f"Item {i}" for i in range(skip, skip + limit) if q in f"Item {i}"]
    else:
        result["results"] = [f"Item {i}" for i in range(skip, skip + limit)]
    return result


@app.get("/items")
def list_items(
    skip: int = 0,
    limit: int = 10,
    q: Optional[str] = None
):
    items = [{"item_id": i, "name": f"Item {i}"} for i in range(skip, skip + limit)]
    if q:
        items = [item for item in items if q.lower() in item["name"].lower()]
    return {"items": items}


# Query param with validation + description for docs
@app.get("/products")
def search_products(
    category: str = Query(
        ...,                        # ← required (no default)
        min_length=3,
        max_length=30,
        description="Product category (required)"
    ),
    min_price: float = Query(
        #  ---> u used only one required value or default

        ...,                        # ← required
        # default=0.0,                   # default value
        
        ge=0.0,                     # greater or equal 0
        description="Minimum price filter"
    ),
    tags: List[str] = Query(        # can accept multiple ?tags=electronics&tags=cheap
        default=[],
        description="List of tags to filter by"
    )
):
    return {
        "category": category,
        "min_price": min_price,
        "tags": tags,
        "found": 42  # fake count
    }

# ------------------------------------------------------------------------------------------------------------------
#Concept 3: Request Body (POST with JSON data)


"""What it is
The request body is data sent in the HTTP request (usually POST, PUT, PATCH) — most often as JSON.
FastAPI uses Pydantic models to automatically:

Parse the JSON
Validate it (types, required fields, constraints like min_length, regex, etc.)
Convert it to Python objects
Generate perfect OpenAPI docs (schemas appear in /docs)
Return nice 422 errors if invalid"""

"""
Why important

Almost every real API needs to create/update data (users, items, orders, etc.)
Pydantic makes validation effortless — no manual checks like if not name
Automatic docs show the expected JSON structure + examples
Type-safe: your IDE knows the structure → better autocompletion & fewer bugs
Handles complex/nested data easily (lists, dicts, sub-models)

When to use

Creating resources: POST /users → send {"name": "Mohamed", "email": "..."}
Updating: PUT /items/42 → send partial or full update
Any endpoint that needs structured data beyond query/path params

"""
# diffrent between query and field and optional and required
#query: ?q=searchterm (string, optional)
#field: {"name": "Mohamed", "age": 30} (JSON   body used in post and put
#optional: q: Optional[str] = None (can be missing or null)
#required: name: str (must be provided in JSON body)

from fastapi import FastAPI, Body
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

# Pydantic model for input (what client sends)
class ItemCreate(BaseModel):
    name:str=Field(...,min_length=3,max_length=50,description="name of the iteams")
    description:Optional[str]=Field(None,max_length=200,description="description of the item")
    price:float=Field(...,gt=0,description="price of the item")
    tags:list[str]=[]


# Separate model for output (can add computed fields, hide secrets, etc.)
class ItemOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    tags: List[str]
    

    class Config:
        from_attributes = True  # useful later with ORMs
        title = "Item Output Model" # for docs
        # anystr_strip_whitespace = True # strip whitespace from strings
        allow_mutation = False # make model immutable

# Fake in-memory storage (we'll replace with DB later)
fake_items_db = []
next_item_id = 1

@app.post("/items3/", response_model=ItemOut, status_code=201)
def create_item(item: ItemCreate):  # ← FastAPI knows to look in body
    global next_item_id
    new_item = {
        "id": next_item_id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "tags": item.tags
    }
    fake_items_db.append(new_item)
    next_item_id += 1
    return new_item


#put method(update) 
@app.put("/items/{item_id}", response_model=ItemOut)
def update_item(item_id: int, item_update: ItemCreate):
    for item in fake_items_db:
        if item["id"] == item_id:
            # Update only provided fields (since ItemCreate has defaults)
            item["name"] = item_update.name
            if item_update.description is not None:
                item["description"] = item_update.description
            item["price"] = item_update.price
            item["tags"] = item_update.tags
            return item
    return {"error": "Item not found"}  # better to raise HTTPException later

# Bonus: Body with extra fields (e.g. embed in root)
@app.post("/items/embed/")
def create_embedded(
    item: ItemCreate = Body(..., embed=True),  # forces {"item": {...}} in JSON
    priority: int = Body(1)
):
    return {"item": item.dict(), "priority": priority}



# ---------------------------------------------------------------------------------------------------
# Concept 4: Response Models & Status Codes
"""What it is

response_model: Tells FastAPI exactly what structure your endpoint should return (using a Pydantic model).
It filters/validates the response data, hides sensitive fields, adds descriptions/examples to docs, and ensures consistent output even if your internal data changes.
status_code: The HTTP status you return (e.g., 201 Created, 404 Not Found).
FastAPI sets defaults (200 OK for GET, 201 for POST), but you can override them.

Why important

Prevents leaking internal data (e.g., don't send passwords back to client)
Makes API docs accurate — /docs shows the exact response schema + examples
Enforces type safety on output (e.g., convert datetime to str)
Better error handling & client expectations (correct 201 vs 200 on create)
Professional APIs always use response models for lists, single items, paginated responses, etc.

When to use

Always for production endpoints (especially POST/PUT/GET lists)
When returning data from DB/ORM → use a model that excludes secrets or adds computed fields
For different responses (e.g., success vs error) → use Union[SuccessModel, ErrorModel]
Custom status: 201 on create, 204 on delete (no body), 404 on not found

Example code (add/update these in your main.py)"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Input model (from previous concept)
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0.0)
    tags: List[str] = []

# Response model - hides internal fields, adds extras
class ItemOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    tags: List[str]
    created_at: str  # we'll format datetime to ISO string
    is_expensive: bool  # computed field example

    class Config:
        from_attributes = True  # allows .from_orm() or dict conversion

# Fake DB with added created_at
fake_items_db = []
next_item_id = 1

# POST with response_model + custom status
@app.post(
    "/items/",
    response_model=ItemOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item",
    response_description="The created item with ID and timestamp"
)
def create_item(item: ItemCreate):
    global next_item_id
    new_item = {
        "id": next_item_id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "tags": item.tags,
        "created_at": datetime.utcnow(),
    }
    fake_items_db.append(new_item)
    next_item_id += 1

    # Convert to dict and add computed field
    item_dict = new_item.copy()
    item_dict["created_at"] = new_item["created_at"].isoformat()
    item_dict["is_expensive"] = new_item["price"] > 1000

    return item_dict  # FastAPI will validate against ItemOut

# GET single item with response_model
@app.get("/items/{item_id}", response_model=ItemOut)
def get_item(item_id: int):
    for item in fake_items_db:
        if item["id"] == item_id:
            item_dict = item.copy()
            item_dict["created_at"] = item["created_at"].isoformat()
            item_dict["is_expensive"] = item["price"] > 1000
            return item_dict
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Item not found",
        headers={"X-Error": "Resource not available"}  # optional custom header
    )

# DELETE with 204 No Content (no response body)
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    for i, item in enumerate(fake_items_db):
        if item["id"] == item_id:
            fake_items_db.pop(i)
            return  # no body returned
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

# Bonus: List response with custom model
class ItemList(BaseModel):
    items: List[ItemOut]
    total: int
    page: int = 1

@app.get("/items", response_model=ItemList)
def list_items(skip: int = 0, limit: int = 10):
    paginated = fake_items_db[skip : skip + limit]
    formatted = []
    for item in paginated:
        d = item.copy()
        d["created_at"] = item["created_at"].isoformat()
        d["is_expensive"] = item["price"] > 1000
        formatted.append(d)
    return {"items": formatted, "total": len(fake_items_db), "page": (skip // limit) + 1}

