# kb_agent.py
import os
import json
import numpy as np
from ai_agent import get_embedding
from typing import List, Dict, Tuple

# Path to KB file
KB_FILE = os.path.join(os.path.dirname(__file__), 'kb.json')

# Cache for KB data and embeddings
_kb_cache: List[Dict] = None
_embeddings_cache: List[List[float]] = None

def _load_kb() -> Tuple[List[Dict], List[List[float]]]:
    """
    Load KB entries and their embeddings.
    Uses caching to avoid recomputation.
    """
    global _kb_cache, _embeddings_cache
    if _kb_cache is None:
        with open(KB_FILE, 'r', encoding='utf-8') as f:
            _kb_cache = json.load(f)
    if _embeddings_cache is None:
        # Compute embeddings for each KB content
        _embeddings_cache = [get_embedding(item['content']) for item in _kb_cache]
    return _kb_cache, _embeddings_cache

def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Compute cosine similarity between two vectors safely.
    """
    a_vec = np.array(a)
    b_vec = np.array(b)
    denom = (np.linalg.norm(a_vec) * np.linalg.norm(b_vec) + 1e-10)
    return float(np.dot(a_vec, b_vec) / denom)

def find_similar(query: str, top_k: int = 3, min_score: float = 0.1) -> List[Dict]:
    """
    Return top_k KB entries most similar to query based on embeddings.

    Args:
        query (str): The search query.
        top_k (int): Maximum number of results to return.
        min_score (float): Minimum cosine similarity threshold.

    Returns:
        List[Dict]: List of dicts with keys:
            - 'id': KB entry ID
            - 'title': KB entry title
            - 'content': KB entry content
            - 'score': similarity score
    """
    kb_entries, embeddings = _load_kb()
    query_vec = get_embedding(query)

    # Compute similarity scores
    scores = [_cosine_similarity(query_vec, e) for e in embeddings]

    # Pair entries with scores and sort descending
    paired = sorted(zip(kb_entries, scores), key=lambda x: x[1], reverse=True)

    # Filter by min_score and limit to top_k, explicitly return id, title, content
    results = []
    for entry, score in paired:
        if score >= min_score:
            results.append({
                "id": entry.get("id"),
                "title": entry.get("title"),
                "content": entry.get("content"),
                "score": float(score)
            })
        if len(results) >= top_k:
            break

    return results
