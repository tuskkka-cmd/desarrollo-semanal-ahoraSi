import os
import secrets
from fastapi import FastAPI, Header, HTTPException, Depends

app = FastAPI(title="Protected Catalog & Shipping API")

# Lee la credencial compartida desde la variable de entorno
INTERNAL_GATEWAY_SECRET = os.getenv("INTERNAL_GATEWAY_SECRET")

if not INTERNAL_GATEWAY_SECRET:
    raise RuntimeError("INTERNAL_GATEWAY_SECRET no esta configurado")

def verify_gateway(x_gateway_secret: str = Header(default="")):
    valid = secrets.compare_digest(x_gateway_secret, INTERNAL_GATEWAY_SECRET)
    if not valid:
        raise HTTPException(
            status_code=403, 
            detail="Solicitud no autorizada desde Gateway"
        )

@app.get("/health")
def health():
    return {"status": "OK", "service": "Protected Backend"}

@app.get("/items", dependencies=[Depends(verify_gateway)])
def get_items(x_authenticated_client: str | None = Header(default=None)):
    return {
        "authenticated_client": x_authenticated_client,
        "items": [
            {"id": 1, "producto": "Laptop Gamer", "stock": 15, "precio": 1200},
            {"id": 2, "producto": "Teclado Mecánico", "stock": 30, "precio": 80}
        ]
    }

@app.get("/shipments", dependencies=[Depends(verify_gateway)])
def get_shipments(x_authenticated_client: str | None = Header(default=None)):
    return {
        "authenticated_client": x_authenticated_client,
        "shipments": [
            {"tracking_id": "TRK-9901", "destino": "Santiago", "estado": "En camino"}
        ]
    }
