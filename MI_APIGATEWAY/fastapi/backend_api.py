from fastapi import FastAPI

app = FastAPI(
    title="Servicio de Catálogo",
    description="Microservicio de inventario de productos tecnológicos"
)

@app.get("/health")
def health():
    return {"status": "OK", "service": "Catalog Service"}

@app.get("/items")
def get_items():
    return {
        "items": [
            {"id": 1, "producto": "Laptop Gamer", "stock": 15, "precio": 1200},
            {"id": 2, "producto": "Teclado Mecánico", "stock": 30, "precio": 80},
            {"id": 3, "producto": "Mouse Inalámbrico", "stock": 50, "precio": 40}
        ]
    }