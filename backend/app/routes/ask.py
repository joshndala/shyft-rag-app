from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from app.services.retriever import search
from app.services.llm import ask_llm, ask_llm_streaming

router = APIRouter()

@router.get("/")
async def ask_question(
    query: str = Query(..., min_length=3, description="The question to answer"),
    stream: bool = Query(True, description="Whether to stream the response")
):
    """
    Retrieves relevant document passages and sends them to the LLM.
    """
    relevant_chunks = search(query)
    if not relevant_chunks:
        raise HTTPException(status_code=404, detail="No relevant documents found")

    # If streaming is requested
    if stream:
        return StreamingResponse(
            ask_llm_streaming(query, relevant_chunks),
            media_type="text/event-stream"
        )
    
    # For non-streaming, extract text from chunks if they are dictionaries
    if relevant_chunks and isinstance(relevant_chunks[0], dict):
        text_chunks = [chunk.get('text', '') for chunk in relevant_chunks]
        context = "\n".join(text_chunks)
    else:
        context = "\n".join(relevant_chunks)
        
    return ask_llm(query, context)