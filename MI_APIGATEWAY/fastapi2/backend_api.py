from fastapi import FastAPI

app = FastAPI(
    title="Servicio de Envíos",
    description="Microservicio de despacho y logística"
)

@app.get("/health")
def health():
    return {"status": "OK", "service": "Shipping Service"}

@app.get("/shipments")
def get_shipments():
    return {
        "shipments": [
            {"tracking_id": "TRK-9901", "destino": "Santiago", "estado": "En camino"},
            {"tracking_id": "TRK-9902", "destino": "Valparaíso", "estado": "Entregado"}
        ]
    }