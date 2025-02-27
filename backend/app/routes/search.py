from fastapi import APIRouter, Query
from app.services.retriever import search

router = APIRouter()

@router.get("/")
async def search_documents(query: str = Query(..., min_length=3)):
    """
    Searches the uploaded documents using hybrid search (BM25 + FAISS).
    """
    results = search(query)
    if not results:
        return {"message": "No relevant documents found"}

    return {"results": results}