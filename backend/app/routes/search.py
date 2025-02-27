from fastapi import APIRouter, Query
from app.services.embedder import document_embedder

router = APIRouter()

@router.get("/")
async def search_documents(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(5, description="Number of results to return"),
    semantic_weight: float = Query(0.7, description="Weight for semantic search (0-1)"),
    keyword_weight: float = Query(0.3, description="Weight for keyword search (0-1)")
):
    """
    Search documents using hybrid semantic and keyword search.
    
    Args:
        query (str): The search query
        top_k (int): Number of results to return
        semantic_weight (float): Weight for semantic search component (0-1)
        keyword_weight (float): Weight for keyword search component (0-1)
        
    Returns:
        list: Top matching results with text and metadata
    """
    # Normalize weights if needed
    total_weight = semantic_weight + keyword_weight
    if total_weight != 1.0:
        semantic_weight = semantic_weight / total_weight
        keyword_weight = keyword_weight / total_weight
        
    results = document_embedder.search(
        query, 
        bm25_weight=keyword_weight, 
        semantic_weight=semantic_weight,
        top_k=top_k
    )
    
    return {"results": results, "query": query, "total_results": len(results)}