import os, json, re
from typing import List, Dict, Optional
from rank_bm25 import BM25Okapi

_TOKEN_RE = re.compile(r"[a-zA-Z0-9_À-ỹ]+")

def _tokenize(s: str) -> List[str]:
    return _TOKEN_RE.findall((s or "").lower())

class JsonBM25:
    def __init__(self):
        self.docs_tokens: List[List[str]] = []
        self.docs_meta: List[Dict] = []
        self.bm25: Optional[BM25Okapi] = None
        self.total_units: int = 0

    def load_dir(self, data_dir: str) -> int:
        docs, metas = [], []
        for name in os.listdir(data_dir):
            if not name.lower().endswith(".json"):
                continue
            title = os.path.splitext(name)[0]
            path = os.path.join(data_dir, name)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for art, obj in data.items():
                heading = obj.get("tiêu_đề", "")

                if isinstance(obj.get("khoản"), dict) and obj["khoản"]:
                    for k, v in obj["khoản"].items():
                        if isinstance(v, dict) and isinstance(v.get("điểm"), dict) and v["điểm"]:
                            for d, text in v["điểm"].items():
                                text = f"{heading}\n{text}".strip()
                                if text:
                                    docs.append(_tokenize(text))
                                    metas.append({
                                        "title": title,
                                        "article": str(art),
                                        "clause": f"{k}.{d}",
                                        "text": text[:800],
                                        "source": f"file://{os.path.abspath(path)}",
                                    })
                        else:
                            text = f"{heading}\n{v}".strip()
                            if text:
                                docs.append(_tokenize(text))
                                metas.append({
                                    "title": title,
                                    "article": str(art),
                                    "clause": str(k),
                                    "text": text,
                                    "source": f"file://{os.path.abspath(path)}",
                                })
                elif isinstance(obj.get("điểm"), dict) and obj["điểm"]:
                    for d, text in obj["điểm"].items():
                        text = f"{heading}\n{text}".strip()
                        if text:
                            docs.append(_tokenize(text))
                            metas.append({
                                "title": title,
                                "article": str(art),
                                "clause": str(d),
                                "text": text[:800],
                                "source": f"file://{os.path.abspath(path)}",
                            })
                else:
                    text = (obj.get("toàn_văn") or heading or "").strip()
                    if text:
                        docs.append(_tokenize(text))
                        metas.append({
                            "title": title,
                            "article": str(art),
                            "clause": None,
                            "text": text[:800],
                            "source": f"file://{os.path.abspath(path)}",
                        })

        self.docs_tokens, self.docs_meta = docs, metas
        self.bm25 = BM25Okapi(self.docs_tokens) if self.docs_tokens else None
        self.total_units = len(self.docs_meta)
        return self.total_units

    def search(self, query: str, top_k: int = 5, allow_titles: Optional[List[str]] = None) -> List[Dict]:
        if not self.bm25 or not (query or "").strip():
            return []
        qtok = _tokenize(query)
        scores = self.bm25.get_scores(qtok)

        ranked = sorted(
            [
                (i, float(scores[i]))
                for i in range(len(scores))
                if not allow_titles or self.docs_meta[i]["title"] in allow_titles
            ],
            key=lambda x: x[1],
            reverse=True,
        )[:top_k]

        out = []
        for i, sc in ranked:
            m = self.docs_meta[i].copy()
            m["score"] = round(sc, 4)
            out.append(m)
        return out

_INDEX = JsonBM25()

def load_index(data_dir: str) -> int:
    return _INDEX.load_dir(data_dir)

def reload_index(data_dir: str) -> int:
    return _INDEX.load_dir(data_dir)

def search(query: str, top_k: int = 5, allow_titles: Optional[List[str]] = None) -> List[Dict]:
    return _INDEX.search(query, top_k=top_k, allow_titles=allow_titles)

def available_units() -> int:
    return _INDEX.total_units
