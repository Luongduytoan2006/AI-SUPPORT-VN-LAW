# tools/build_vector_index.py
import os, json, argparse, sys, pathlib, time, hashlib
from typing import Dict, List

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.llm_client import embed_ollama

def _unit_key(it: Dict) -> str:
    h = hashlib.md5((it.get("text") or "").encode("utf-8")).hexdigest()
    return f"{it.get('title')}|{it.get('article')}|{it.get('clause')}|{h}"

def _load_existing_keys(index_path: str) -> set:
    keys = set()
    if not os.path.exists(index_path):
        return keys
    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                keys.add(_unit_key(obj))
            except Exception:
                continue
    return keys

def iter_units(data_dir):
    for name in os.listdir(data_dir):
        if not name.lower().endswith(".json"): continue
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
                            txt = f"{heading}\n{text}".strip()
                            if txt:
                                yield {"title": title, "article": str(art), "clause": f"{k}.{d}",
                                       "text": txt, "source": f"file://{os.path.abspath(path)}"}
                    else:
                        txt = f"{heading}\n{v}".strip()
                        if txt:
                            yield {"title": title, "article": str(art), "clause": str(k),
                                   "text": txt, "source": f"file://{os.path.abspath(path)}"}
            elif isinstance(obj.get("điểm"), dict) and obj["điểm"]:
                for d, text in obj["điểm"].items():
                    txt = f"{heading}\n{text}".strip()
                    if txt:
                        yield {"title": title, "article": str(art), "clause": str(d),
                               "text": txt, "source": f"file://{os.path.abspath(path)}"}
            else:
                txt = (obj.get("toàn_văn") or heading or "").strip()
                if txt:
                    yield {"title": title, "article": str(art), "clause": None,
                           "text": txt, "source": f"file://{os.path.abspath(path)}"}

def embed_batch(texts: List[str], retries: int = 3, backoff: float = 2.0):
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            return embed_ollama(texts)
        except Exception as e:
            last_err = e
            if attempt < retries:
                sleep_s = backoff * attempt
                print(f"⚠️ Batch lỗi ({e}). Thử lại {attempt}/{retries} sau {sleep_s:.1f}s...")
                time.sleep(sleep_s)
            else:
                raise last_err

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--index", default="index")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--truncate-chars", type=int, default=1000)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    os.makedirs(args.index, exist_ok=True)
    out_path = os.path.join(args.index, "index.jsonl")

    existing = _load_existing_keys(out_path) if args.resume else set()
    if existing:
        print(f"🔁 Resume: phát hiện {len(existing)} entries trong {out_path}")

    total = sum(1 for _ in iter_units(args.data))
    print(f"📦 Tổng unit: {total}")

    written = 0
    pending: List[Dict] = []
    with open(out_path, "a", encoding="utf-8") as fout:
        for it in iter_units(args.data):
            key = _unit_key(it)
            if key in existing: 
                continue
            if args.truncate_chars and args.truncate_chars > 0:
                it["text"] = it["text"][:args.truncate_chars]
            pending.append(it)
            if len(pending) >= args.batch_size:
                texts = [x["text"] for x in pending]
                vecs = embed_batch(texts)
                for obj, v in zip(pending, vecs):
                    if not isinstance(v, list) or not v or not isinstance(v[0], (int, float)):
                        raise RuntimeError("Embedding rỗng hoặc không hợp lệ.")
                    obj["embedding"] = v
                    fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
                written += len(pending)
                print(f"✅ Ghi thêm {len(pending)} (tổng {written}).")
                pending.clear()

        if pending:
            texts = [x["text"] for x in pending]
            vecs = embed_batch(texts)
            for obj, v in zip(pending, vecs):
                if not isinstance(v, list) or not v or not isinstance(v[0], (int, float)):
                    raise RuntimeError("Embedding rỗng hoặc không hợp lệ (flush).")
                obj["embedding"] = v
                fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
            written += len(pending)
            print(f"✅ Ghi thêm {len(pending)} (tổng {written}).")

    print(f"🎉 Xong. File: {out_path} (mới ghi {written} entries).")
    print("💡 Bật EMBEDDINGS_ENABLED=true trong .env để dùng vector search.")

if __name__ == "__main__":
    main()
