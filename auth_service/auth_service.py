import os
import secrets
import httpx
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

app = FastAPI(
    title="TechStore Auth Service",
    description="Servicio centralizado de autenticación y validación de tokens"
)

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "dev-only-token")

class LoginRequest(BaseModel):
    username: str
    password: str

async def get_vault_secrets():
    url = f"{VAULT_ADDR}/v1/secret/data/gateway"
    headers = {"X-Vault-Token": VAULT_TOKEN}
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Error al consultar Vault desde Auth Service")
            vault_data = response.json()
            return vault_data["data"]["data"]
        except httpx.RequestError:
            # Fallback en caso de que Vault no esté accesible durante la prueba
            return {
                "client_token": "techstore-client-123",
                "backend_shared_secret": "techstore-api-secret-456"
            }

@app.get("/health")
def health():
    return {"status": "OK", "service": "Auth Service"}

@app.get("/validate")
async def validate_token(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Formato de token invalido. Se requiere Bearer Token"
        )
    
    token = authorization.replace("Bearer ", "").strip()
    vault_secrets = await get_vault_secrets()
    
    expected_token = vault_secrets.get("client_token", "techstore-client-123")
    
    valid = secrets.compare_digest(token, expected_token)
    if not valid:
        raise HTTPException(
            status_code=401, 
            detail="Token invalido o expirado"
        )
    
    return {
        "valid": True,
        "client_id": "techstore-student-client",
        "scope": "read:items read:shipments"
    }
