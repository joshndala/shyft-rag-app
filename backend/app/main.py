from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload, search, ask

app = FastAPI(title="RAG Backend")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routes
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(ask.router, prefix="/ask", tags=["Ask"])

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG API!"}