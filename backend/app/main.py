from fastapi import FastAPI
from app.routes import upload, search, ask

app = FastAPI(title="RAG Backend")

# Include routes
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(ask.router, prefix="/ask", tags=["Ask"])

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG API!"}