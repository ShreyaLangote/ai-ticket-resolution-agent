\
import numpy as np
from ai_agent import get_embedding

SIMILARITY_THRESHOLD = 0.82

def cosine(a,b):
    a = np.array(a); b = np.array(b)
    return float((a @ b) / (np.linalg.norm(a)*np.linalg.norm(b)+1e-10))

def find_duplicate_groups(tickets):
    texts = [t['description'] for t in tickets]
    embeddings = [get_embedding(t) for t in texts]
    n = len(tickets)
    groups = []
    visited = set()
    for i in range(n):
        if i in visited: continue
        group = [tickets[i]['id']]
        for j in range(i+1, n):
            sim = cosine(embeddings[i], embeddings[j])
            if sim >= SIMILARITY_THRESHOLD:
                group.append(tickets[j]['id'])
                visited.add(j)
        if len(group) > 1:
            groups.append(group)
    return groups
