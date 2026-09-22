from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(
    title="TechStore API Gateway",
    description="Orquestador central para e-commerce"
)

CATALOG_SERVICE_URL = "http://localhost:9000"
SHIPPING_SERVICE_URL = "http://localhost:9001"

@app.get("/health")
def gateway_health():
    return {"status": "OK", "service": "TechStore Gateway"}

# Enrutamiento al Servicio 1 (Puerto 9000)
@app.get("/api/v1/items")
async def proxy_items():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CATALOG_SERVICE_URL}/items")
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Servicio de Catálogo no disponible")

# Enrutamiento al Servicio 2 (Puerto 9001)
@app.get("/api/v1/shipments")
async def proxy_shipments():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SHIPPING_SERVICE_URL}/shipments")
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Servicio de Envíos no disponible")