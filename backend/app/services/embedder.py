from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from rank_bm25 import BM25Okapi
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