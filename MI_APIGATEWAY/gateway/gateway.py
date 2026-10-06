import os
import httpx
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI(title="Secure TechStore API Gateway con Auth Service")

security = HTTPBearer(auto_error=False)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:7000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:9000")
BACKEND_SECRET = os.getenv("INTERNAL_GATEWAY_SECRET", "techstore-api-secret-456")

async def authenticate_via_auth_service(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Bearer token requerido")
    
    token = credentials.credentials
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            res = await client.get(f"{AUTH_SERVICE_URL}/validate", headers=headers)
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Servicio de Autenticacion no disponible")
            
        if res.status_code != 200:
            raise HTTPException(status_code=401, detail="Token rechazado por Auth Service")
        
        auth_data = res.json()
        return {
            "client_id": auth_data.get("client_id", "techstore-client"),
            "backend_secret": BACKEND_SECRET
        }

@app.get("/health")
def health():
    return {"status": "OK", "service": "API Gateway"}

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(path: str, request: Request, auth: dict = Depends(authenticate_via_auth_service)):
    target_url = f"{BACKEND_URL}/{path}"
    body = await request.body()
    
    gateway_headers = {
        "X-Gateway-Secret": auth["backend_secret"],
        "X-Authenticated-Client": auth["client_id"]
    }
    
    content_type = request.headers.get("content-type")
    if content_type:
        gateway_headers["content-type"] = content_type
        
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            upstream = await client.request(
                method=request.method,
                url=target_url,
                params=request.query_params,
                content=body,
                headers=gateway_headers
            )
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Backend no disponible")
        
    response_headers = {}
    if "content-type" in upstream.headers:
        response_headers["content-type"] = upstream.headers["content-type"]
        
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers
    )
