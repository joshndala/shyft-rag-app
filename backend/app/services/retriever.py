from app.services.embedder import document_embedder

def search(query, top_k=5):
    """
    Performs hybrid search on the indexed documents.
    
    This is now a thin wrapper around the embedder's search method
    to maintain backward compatibility with existing code.
    
    Args:
        query (str): The search query
        top_k (int): Number of results to return
        
    Returns:
        list: Top matching results with text and metadata
    """
    return document_embedder.search(query, top_k=top_k)

def load_indexes():
    """
    Load indexes from disk.
    
    This is now a thin wrapper around the embedder's load_indexes method
    to maintain backward compatibility with existing code.
    """
    document_embedder.load_indexes()

# Make sure embedder's indexes are loaded
load_indexes()