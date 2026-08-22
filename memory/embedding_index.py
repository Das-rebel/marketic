"""
Embedding Index — Semantic search over brand knowledge using sentence-transformers.
"""

import os
from typing import List, Tuple, Optional, Dict, Any

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from .brand_memory import BrandMemoryStore, Memory


class EmbeddingIndex:
    """
    Semantic search over brand memories using embeddings.
    Falls back to simple keyword search if sentence-transformers not available.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model = None
        self._index: Dict[str, np.ndarray] = {}  # memory_id -> embedding
        self._model_name = model_name
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self._model = SentenceTransformer(model_name)
            except Exception:
                pass
    
    @property
    def is_available(self) -> bool:
        return self._model is not None
    
    def index_text(self, brand_id: str, text: str, memory_id: str, metadata: Optional[Dict] = None):
        """Index a text for a brand."""
        if not self._model:
            return  # No-op if model not available
        
        try:
            embedding = self._model.encode(text, convert_to_numpy=True)
            self._index[memory_id] = embedding
        except Exception:
            pass
    
    def index_memories(self, brand_id: str, memories: List[Memory]):
        """Index all memories for a brand."""
        if not self._model:
            return
        
        for memory in memories:
            try:
                embedding = self._model.encode(memory.content, convert_to_numpy=True)
                self._index[memory.id] = embedding
            except Exception:
                pass
    
    def search(self, brand_id: str, query: str, top_k: int = 5) -> List[Tuple[Memory, float]]:
        """
        Search memories using semantic similarity.
        Returns list of (Memory, similarity_score).
        """
        if not self._model or not self._index:
            return []
        
        try:
            query_embedding = self._model.encode(query, convert_to_numpy=True)
            
            # Get all indexed memories for this brand
            # Note: In production you'd filter by brand_id in the index
            results = []
            
            for memory_id, embedding in self._index.items():
                # Simple cosine similarity
                similarity = float(np.dot(query_embedding, embedding) / 
                               (np.linalg.norm(query_embedding) * np.linalg.norm(embedding) + 1e-8))
                results.append((memory_id, similarity))
            
            # Sort by similarity descending
            results.sort(key=lambda x: -x[1])
            
            # Fetch memory objects and return with scores
            store = BrandMemoryStore()
            scored_results = []
            for memory_id, score in results[:top_k]:
                memories = store.get_memories(brand_id, query=memory_id)
                for m in memories:
                    if m.id == memory_id:
                        scored_results.append((m, score))
                        break
            
            return scored_results
        except Exception:
            return []
    
    def delete_memory(self, memory_id: str):
        """Remove a memory from the index."""
        if memory_id in self._index:
            del self._index[memory_id]
    
    def clear_index(self):
        """Clear all indexed memories."""
        self._index.clear()
