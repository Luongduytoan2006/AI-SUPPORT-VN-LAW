import os, json, math
from typing import List, Dict, Optional
from core.llm_client import embed_ollama

_STORE: List[Dict] = []

def load_vector_store(index_path: str = "index/index.jsonl") -> int:
    global _STORE
    _STORE = []
    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line.strip())
            emb = obj.get("embedding", [])
            if isinstance(emb, list) and emb and isinstance(emb[0], (int, float)):
                _STORE.append(obj)
    print(f"[vector] loaded {len(_STORE)} units from {index_path}")
    return len(_STORE)

def _cos(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a)) + 1e-8
    nb = math.sqrt(sum(y*y for y in b)) + 1e-8
    return dot/(na*nb)

def vector_search(query: str, top_k: int = 5, allow_titles: Optional[List[str]] = None, embed_model: Optional[str] = None):
    if not _STORE or not query.strip():
        return []
    qv = embed_ollama([query], model=embed_model)[0]
    scored = []
    for it in _STORE:
        if allow_titles and it.get("title") not in allow_titles:
            continue
        s = _cos(qv, it["embedding"])
        scored.append((s, it))
    scored.sort(key=lambda x: x[0], reverse=True)
    out = []
    for s, it in scored[:top_k]:
        out.append({
            "title": it["title"], "article": it["article"], "clause": it["clause"],
            "text": it["text"], "source": it["source"], "score": float(s)
        })
    return out
