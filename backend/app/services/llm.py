import requests
import json
import asyncio
from app.config import config

OPENROUTER_API_KEY = config.OPENROUTER_API_KEY

def create_prompt(question, context):
    """Format the prompt for the LLM."""
    return f"""Answer the question based only on the provided context. If the context doesn't contain the information needed to answer the question, say "I don't have enough information to answer this question."

Context:
{context}

Question: {question}

Answer:"""

async def ask_llm_streaming(question, context_chunks):
    """
    Stream responses from OpenRouter.
    
    Args:
        question (str): User's question
        context_chunks (list): List of relevant text chunks from search
        
    Yields:
        str: Text chunks formatted as Server-Sent Events
    """
    # Extract text from each context chunk if they are dictionaries
    if context_chunks and isinstance(context_chunks[0], dict):
        text_chunks = [chunk.get('text', '') for chunk in context_chunks]
    else:
        text_chunks = context_chunks
    
    # Format context with clear separations
    context = "\n\n---\n\n".join(text_chunks)
    
    # Format prompt with instructions
    prompt = create_prompt(question, context)
    
    # Prepare the API request
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mistralai/mixtral-8x7b-instruct",  # You can adjust the model
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that provides accurate information based on context from retrieved documents."},
            {"role": "user", "content": prompt}
        ],
        "stream": True,
        "temperature": 0.1  # Lower temperature for more factual responses
    }
    
    try:
        # Make the request in a way that can be properly awaited
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=data,
            headers=headers,
            stream=True
        )
        
        # Check for errors
        if response.status_code != 200:
            error_msg = f"Error from OpenRouter API: {response.status_code} - {response.text}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
            return
            
        # Process the streaming response
        for line in response.iter_lines():
            if line:
                # Remove the "data: " prefix if present
                line_text = line.decode('utf-8')
                if line_text.startswith("data: "):
                    line_text = line_text[6:]  # Remove "data: " prefix
                
                # Skip empty lines or "[DONE]"
                if line_text == "[DONE]" or not line_text.strip():
                    continue
                    
                try:
                    # Parse the JSON response
                    json_data = json.loads(line_text)
                    
                    # Extract content if available
                    if "choices" in json_data and json_data["choices"]:
                        choice = json_data["choices"][0]
                        if "delta" in choice and "content" in choice["delta"]:
                            content = choice["delta"]["content"]
                            if content:
                                # Yield as server-sent event
                                yield f"data: {json.dumps({'content': content})}\n\n"
                                await asyncio.sleep(0.01)  # Small delay for smoother streaming
                except json.JSONDecodeError:
                    # Skip lines that aren't valid JSON
                    continue
                
        # End of stream marker
        yield f"data: {json.dumps({'content': '', 'end': True})}\n\n"
        
    except Exception as e:
        # Handle any exceptions
        error_msg = f"Error generating response: {str(e)}"
        yield f"data: {json.dumps({'error': error_msg})}\n\n"
        print(f"❌ {error_msg}", flush=True)

def ask_llm(question, context):
    """
    Non-streaming version for backwards compatibility.
    Generates a complete response from OpenRouter.
    
    Args:
        question (str): User's question
        context (str): Context information
        
    Returns:
        dict: The LLM's response
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = create_prompt(question, context)
    
    data = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that provides accurate information based on context from retrieved documents."},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=data,
            headers=headers
        )
        
        response_data = response.json()
        
        if "choices" in response_data and response_data["choices"]:
            answer = response_data["choices"][0]["message"]["content"]
            return {"answer": answer}
        else:
            return {"error": "Failed to get response from LLM"}
            
    except Exception as e:
        return {"error": f"Error: {str(e)}"}