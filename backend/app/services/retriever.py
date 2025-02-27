from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
from app.config import config

bm25_corpus = []
bm25_index = None
faiss_index = None

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def store_text_embeddings(text):
    """Stores document text in BM25 and FAISS index."""
    global bm25_index, faiss_index, bm25_corpus

    texts = text.split("\n")  # Split into chunks
    bm25_corpus = texts
    tokenized_corpus = [doc.split() for doc in texts]
    
    # Create BM25 index
    bm25_index = BM25Okapi(tokenized_corpus)

    # Create FAISS index
    embeddings = embedder.encode(texts)
    faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
    faiss_index.add(np.array(embeddings))

def search(query):
    """Performs hybrid search using BM25 and FAISS."""
    if not bm25_index or not faiss_index:
        return {"error": "No documents indexed yet"}

    # BM25 search
    keyword_results = bm25_index.get_top_n(query.split(), bm25_corpus, n=5)

    # Semantic search using FAISS
    query_embedding = embedder.encode([query])
    _, semantic_results = faiss_index.search(np.array(query_embedding), k=5)

    # Merge and return unique results
    final_results = list(set(keyword_results + [bm25_corpus[idx] for idx in semantic_results[0]]))
    return final_results