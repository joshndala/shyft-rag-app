from fastapi import APIRouter, Query
from app.services.retriever import search
from app.services.llm import ask_llm

router = APIRouter()

@router.get("/")
async def ask_question(query: str = Query(..., min_length=3)):
    """Retrieves relevant document passages and sends them to the LLM."""
    relevant_chunks = search(query)
    if not relevant_chunks:
        return {"error": "No relevant documents found"}

    context = "\n".join(relevant_chunks)
    return ask_llm(query, context)