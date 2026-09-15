from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from bson import ObjectId

# 1. Conexión a MongoDB
MONGODB_URI = "mongodb://localhost:27017"
DB_NAME = "bdunab2"
COLL_NAME = "items"

client: Optional[AsyncIOMotorClient] = None
db = None
coll = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db, coll
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    coll = db[COLL_NAME]
    yield
    if client:
        client.close()

app = FastAPI(title="Craft & Beer API", lifespan=lifespan)

# 2. Modelos Pydantic
class Item(BaseModel):
    nombre: str = Field(..., min_length=1)
    precio: float = Field(..., gt=0)
    tags: List[str] = Field(default_factory=list)
    activo: bool = Field(default=True)

class ItemIn(Item):
    pass

class ItemOut(Item):
    id: str

def doc_to_itemout(doc: dict) -> ItemOut:
    return ItemOut(
        id=str(doc["_id"]),
        nombre=doc["nombre"],
        precio=doc["precio"],
        tags=doc.get("tags", []),
        activo=doc.get("activo", True)
    )

# 3. Endpoints REST
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok"}

@app.get("/items", response_model=List[ItemOut], status_code=status.HTTP_200_OK)
async def listar_items(
    q: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    query = {}
    if q:
        query["nombre"] = {"\(regex": q, "\)options": "i"}
    cursor = coll.find(query).skip(skip).limit(limit)
    items = []
    async for doc in cursor:
        items.append(doc_to_itemout(doc))
    return items

@app.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def crear_item(item: ItemIn):
    nuevo_doc = item.model_dump()
    res = await coll.insert_one(nuevo_doc)
    doc_creado = await coll.find_one({"_id": res.inserted_id})
    return doc_to_itemout(doc_creado)

@app.get("/items/{item_id}", response_model=ItemOut, status_code=status.HTTP_200_OK)
async def obtener_item(item_id: str):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID invalido")
    doc = await coll.find_one({"_id": ObjectId(item_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado")
    return doc_to_itemout(doc)

@app.put("/items/{item_id}", response_model=ItemOut, status_code=status.HTTP_200_OK)
async def actualizar_item(item_id: str, item: ItemIn):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID invalido")
    res = await coll.update_one({"_id": ObjectId(item_id)}, {"$set": item.model_dump()})
    if res.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado")
    doc_actualizado = await coll.find_one({"_id": ObjectId(item_id)})
    return doc_to_itemout(doc_actualizado)

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_item(item_id: str):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID invalido")
    res = await coll.delete_one({"_id": ObjectId(item_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado")
    return None