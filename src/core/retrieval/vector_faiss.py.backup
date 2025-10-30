import os, json, pathlib
from typing import List, Dict, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

try:
    import faiss
except Exception:
    faiss = None

ROOT = pathlib.Path(__file__).resolve().parents[1].parents[0]
INDEX_DIR = pathlib.Path(os.getenv("INDEX_DIR", "index"))

_model: Optional[SentenceTransformer] = None
_index = None
_metas: List[Dict] = []
_matrix: Optional[np.ndarray] = None

def _load_metas() -> List[Dict]:
    path = INDEX_DIR / "meta.jsonl"
    metas = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            metas.append(json.loads(line))
    return metas

def load_vector_index(embedding_model: str = "BAAI/bge-m3") -> Tuple[int, bool]:
    global _model, _index, _metas, _matrix
    _metas = _load_metas()
    _model = SentenceTransformer(embedding_model)
    faiss_path = INDEX_DIR / "faiss.index"
    if faiss is not None and faiss_path.exists():
        _index = faiss.read_index(str(faiss_path))
        _matrix = None
        return (len(_metas), True)
    npy_path = INDEX_DIR / "embeddings.npy"
    if npy_path.exists():
        _matrix = np.load(npy_path).astype("float32")
        _index = None
        return (len(_metas), False)
    raise FileNotFoundError("No FAISS index or embeddings.npy found in index/")

def vector_search(query: str, top_k: int = 6, allow_titles: Optional[List[str]] = None) -> List[Dict]:
    global _model, _index, _metas, _matrix
    if not query.strip() or _model is None:
        return []
    qv = _model.encode([query], normalize_embeddings=True, convert_to_numpy=True).astype("float32")[0]

    candidates: List[Tuple[int, float]] = []
    if _index is not None:
        D, I = _index.search(qv.reshape(1, -1), top_k * 4)
        for i, s in zip(I[0].tolist(), D[0].tolist()):
            if i < 0: continue
            candidates.append((i, float(s)))
    elif _matrix is not None:
        sims = (_matrix @ qv)
        idx = np.argsort(-sims)[: top_k * 4]
        candidates = [(int(i), float(sims[i])) for i in idx]
    else:
        return []

    out: List[Dict] = []
    for i, sc in candidates:
        m = _metas[i]
        if allow_titles and m["title"] not in allow_titles:
            continue
        out.append({
            "title": m["title"], "article": m["article"], "clause": m.get("clause"),
            "text": m["text"][:800], "source": m["source"], "vscore": round(sc, 4)
        })
        if len(out) >= top_k:
            break
    return out
