import faiss
import numpy as np
import json
import os
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

class DocumentEmbedder:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize the document embedder with specified model."""
        # Paths for saving index
        self.BM25_FILE = "data/bm25_corpus.json"
        self.METADATA_FILE = "data/chunk_metadata.json"
        self.FAISS_FILE = "data/faiss.index"
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Initialize embedding model
        self.embedder = SentenceTransformer(model_name)
        
        # Initialize indices
        self.bm25_corpus = []
        self.chunk_metadata = []
        self.bm25_index = None
        self.faiss_index = None
        
        # Load existing indices if available
        self.load_indexes()

    def chunk_text(self, text, chunk_size=512, overlap=50):
        """Split text into overlapping chunks of roughly equal size."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.strip()) > 0:
                chunks.append(chunk)
        
        # If no chunks were created or text is very short, use the original text
        if not chunks and text.strip():
            chunks = [text]
            
        return chunks

    def load_indexes(self):
        """Loads BM25 and FAISS indexes from disk if available."""
        print("🔄 Loading indexes from disk...", flush=True)

        # Load BM25 corpus
        if os.path.exists(self.BM25_FILE):
            with open(self.BM25_FILE, "r", encoding="utf-8") as f:
                self.bm25_corpus = json.load(f)
            print(f"✅ Loaded BM25 corpus with {len(self.bm25_corpus)} documents.", flush=True)

            tokenized_corpus = [doc.split() for doc in self.bm25_corpus]
            self.bm25_index = BM25Okapi(tokenized_corpus)
            print("✅ BM25 index rebuilt.", flush=True)
        else:
            print("❌ No BM25 corpus found.", flush=True)

        # Load chunk metadata
        if os.path.exists(self.METADATA_FILE):
            with open(self.METADATA_FILE, "r", encoding="utf-8") as f:
                self.chunk_metadata = json.load(f)
            print(f"✅ Loaded chunk metadata for {len(self.chunk_metadata)} chunks.", flush=True)
        else:
            print("❌ No chunk metadata found.", flush=True)

        # Load FAISS index
        if os.path.exists(self.FAISS_FILE):
            self.faiss_index = faiss.read_index(self.FAISS_FILE)
            print(f"✅ FAISS index loaded with {self.faiss_index.ntotal} vectors.", flush=True)
        else:
            print("❌ No FAISS index found.", flush=True)

    def store_text_embeddings(self, text, document_id=None, filename=None):
        """Stores document text in BM25 and FAISS index with document tracking."""
        if not text.strip():
            print("❌ No valid text to index!", flush=True)
            return

        # Create chunks with better strategy
        chunks = self.chunk_text(text)
        print(f"✅ Created {len(chunks)} chunks from document.", flush=True)
        
        # If adding to existing corpus, get the current length as starting index
        starting_index = len(self.bm25_corpus)
        
        # Store chunks and metadata
        for i, chunk in enumerate(chunks):
            # Add to BM25 corpus
            self.bm25_corpus.append(chunk)
            
            # Create and store metadata for this chunk
            chunk_info = {
                "document_id": document_id or filename or f"doc_{len(self.chunk_metadata)}",
                "chunk_index": i,
                "global_index": starting_index + i,
                "chunk_size": len(chunk),
                "word_count": len(chunk.split())
            }
            self.chunk_metadata.append(chunk_info)

        # Rebuild BM25 index with all documents
        tokenized_corpus = [doc.split() for doc in self.bm25_corpus]
        self.bm25_index = BM25Okapi(tokenized_corpus)
        print("✅ BM25 indexing complete.", flush=True)

        # Save BM25 corpus
        with open(self.BM25_FILE, "w", encoding="utf-8") as f:
            json.dump(self.bm25_corpus, f)
        print("✅ BM25 corpus saved to disk.", flush=True)
        
        # Save chunk metadata
        with open(self.METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.chunk_metadata, f)
        print("✅ Chunk metadata saved to disk.", flush=True)

        # Create or update FAISS index
        new_embeddings = self.embedder.encode(chunks)
        
        if self.faiss_index is None:
            # Create new index
            self.faiss_index = faiss.IndexFlatL2(new_embeddings.shape[1])
            self.faiss_index.add(np.array(new_embeddings))
        else:
            # Add to existing index
            self.faiss_index.add(np.array(new_embeddings))
        
        print(f"✅ FAISS index updated. Total vectors: {self.faiss_index.ntotal}", flush=True)

        # Save FAISS index
        faiss.write_index(self.faiss_index, self.FAISS_FILE)
        print("✅ FAISS index saved to disk.", flush=True)
        
        return len(chunks)

    def search(self, query, bm25_weight=0.3, semantic_weight=0.7, top_k=5):
        """Performs weighted hybrid search using BM25 and FAISS."""
        if not self.bm25_index or not self.faiss_index or not self.bm25_corpus:
            print("❌ No documents indexed yet.", flush=True)
            return {"error": "No documents indexed yet"}

        print(f"🔍 Searching for: {query}", flush=True)
        print(f"📂 Total Documents Indexed: {len(self.bm25_corpus)}", flush=True)

        # Get BM25 scores for all documents
        bm25_scores = self.bm25_index.get_scores(query.split())
        
        # Normalize BM25 scores to [0,1] range
        bm25_scores_norm = bm25_scores / np.max(bm25_scores) if np.max(bm25_scores) > 0 else bm25_scores
        
        # Get semantic search results
        query_embedding = self.embedder.encode([query])
        D, I = self.faiss_index.search(np.array(query_embedding), k=min(len(self.bm25_corpus), 20))
        
        # Normalize semantic scores (convert distances to similarities)
        # FAISS returns L2 distances, so smaller is better. Convert to similarity where higher is better.
        semantic_scores = 1 - (D[0] / np.max(D[0])) if np.max(D[0]) > 0 else 1 - D[0]
        
        # Combine scores using weighted approach
        combined_scores = {}
        
        # Add BM25 scores
        for i, score in enumerate(bm25_scores_norm):
            combined_scores[i] = bm25_weight * score
        
        # Add semantic scores
        for idx_pos, idx in enumerate(I[0]):
            if idx in combined_scores:
                combined_scores[idx] += semantic_weight * semantic_scores[idx_pos]
            else:
                combined_scores[idx] = semantic_weight * semantic_scores[idx_pos]
        
        # Get top results
        top_indices = sorted(combined_scores.keys(), key=lambda x: combined_scores[x], reverse=True)[:top_k]
        
        # Retrieve text and metadata for top results
        top_results = []
        for idx in top_indices:
            if idx < len(self.bm25_corpus):
                result = {
                    "text": self.bm25_corpus[idx],
                    "score": combined_scores[idx],
                }
                
                # Find and add metadata if available
                for meta in self.chunk_metadata:
                    if meta.get("global_index") == idx:
                        result["metadata"] = meta
                        break
                
                top_results.append(result)
        
        print(f"✅ Found {len(top_results)} results.", flush=True)
        
        return top_results

# Create a singleton instance to be imported by other modules
document_embedder = DocumentEmbedder()

# For backwards compatibility with existing code
def store_text_embeddings(text, document_id=None, filename=None):
    return document_embedder.store_text_embeddings(text, document_id, filename)

def search(query, top_k=5):
    return document_embedder.search(query, top_k=top_k)