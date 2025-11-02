from __future__ import annotations
from typing import List, Dict
import os, re, time, pathlib

# BM25
from core.retrieval.bm25_json import (
    load_index as bm25_load_index,
    reload_index as bm25_reload_index,
    search as bm25_search,
    available_units,
)
# Vector JSONL
from core.retrieval.vector_jsonl import load_vector_store, vector_search

from core.settings import Settings
from core.llm_client import chat
from core.utils import Heartbeat, lap_timer, print_step_timing, print_timing_info, check_internet_connection, print_status_info

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROMPT_PATH = ROOT / "prompts" / "final_answer.txt"

# ---- Heuristics rút gọn để thu hẹp phạm vi theo từ khóa ----
# NOTE: Đây là ví dụ cho dữ liệu mẫu pháp luật Việt Nam
# Nếu bạn dùng dữ liệu riêng, hãy tùy chỉnh hoặc comment lại phần này
_KEY2TITLE = [
    (re.compile(r"\b(shtt|sở\s*hữu\s*trí\s*tuệ|nhãn\s*hiệu|bản\s*quyền|sáng\s*chế|bí\s*mật\s*kinh\s*doanh)\b", re.I), "so_huu_tri_tue"),
    (re.compile(r"\b(đất\s*đai|sổ\s*đỏ|giấy\s*chứng\s*nhận)\b", re.I), "dat_dai"),
    (re.compile(r"\b(lao\s*động|hợp\s*đồng\s*lao\s*động|sa\s*thải)\b", re.I), "lao_dong"),
    (re.compile(r"\b(hôn\s*nhân|ly\s*hôn|con\s*chung)\b", re.I), "hon_nhan"),
    (re.compile(r"\b(giao\s*thông|nồng\s*độ\s*cồn|xử\s*phạt|mức\s*phạt|phạt)\b", re.I), "giao_thong_duong_bo"),
    (re.compile(r"\b(an\s*ninh\s*mạng|không\s*gian\s*mạng)\b", re.I), "an_ninh_mang"),
]
# Để tắt tính năng này (tìm kiếm toàn bộ dữ liệu), đặt: _KEY2TITLE = []

def _restrict_titles_for_penalty(all_titles: List[str]) -> List[str]:
    pref = [t for t in all_titles if t.startswith("xu_phat_")]
    return pref[:2] if pref else []

def _pick_titles(question: str, data_dir: str) -> List[str]:
    titles = {os.path.splitext(n)[0] for n in os.listdir(data_dir) if n.lower().endswith(".json")}
    if re.search(r"\b(mức\s*phạt|xử\s*phạt|phạt|tiền\s*phạt)\b", (question or ""), re.I):
        pref = _restrict_titles_for_penalty(sorted(titles))
        if pref:
            return pref
    chosen: List[str] = [name for (rg, name) in _KEY2TITLE if rg.search(question or "") and name in titles]
    return list(dict.fromkeys(chosen))[:2]

def _format_context(hits: List[Dict], max_chars: int) -> str:
    buf, total = [], 0
    for h in hits:
        head = f"[{h['title']} | Điều {h['article']}" + (f", Khoản {h.get('clause')}]" if h.get('clause') else "]")
        body = f"{head}\n{h.get('text','')}\nSOURCE: {h.get('source')}\n"
        if total + len(body) > max_chars:
            break
        buf.append(body)
        total += len(body)
    return "\n---\n".join(buf)

def _direct_cite(hits: List[Dict]) -> Dict:
    bullets = []
    for h in hits:
        tag = f"[{h['title']} | Điều {h['article']}" + (f", Khoản {h.get('clause')}]" if h.get('clause') else "]")
        score = h.get("score") if h.get("score") is not None else h.get("vscore")
        bullets.append(f"- **{tag}** — {h.get('text','')[:220].strip()} … (score: {round(float(score or 0.0),4)})")
    answer = (
        "# Kết quả trích dẫn nhanh\n" + "\n".join(bullets) +
        "\n\n> *Lưu ý:* Đây là trích dẫn tự động; để phân tích tình huống, bật chế độ phân tích."
    )
    return {"mode": "direct-cite", "answer": answer, "citations": hits, "used_context": True}

def _rag_answer(question: str, ctx: str, settings: Settings) -> str:
    try:
        sys_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    except Exception:
        sys_prompt = (
            "Bạn là Luật sư tư vấn pháp luật Việt Nam chuyên nghiệp. "
            "Sử dụng CONTEXT để tư vấn chính xác và thực tiễn. "
            "Mỗi kết luận phải có trích dẫn [title | Điều X, Khoản Y]. "
            "Trả lời đầy đủ, chi tiết như một luật sư chuyên nghiệp. "
            "Nếu thiếu thông tin, ghi 'Cần tham khảo thêm' và nêu rõ cần gì. "
            "Dùng markdown có cấu trúc rõ ràng."
        )
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"CONTEXT:\n{ctx}\n\nCÂU HỎI: {question}"},
    ]
    model       = getattr(settings, "llm_model",  os.getenv("LLM_MODEL", "qwen2.5:3b-instruct"))
    max_tokens  = getattr(settings, "max_tokens", int(os.getenv("MAX_TOKENS", "512")))
    temperature = getattr(settings, "temperature", 0.0)

    hb_sec = float(os.getenv("HEARTBEAT_SEC", "60"))
    with Heartbeat("Đang gọi LLM", every=hb_sec):
        return chat(messages, model=model, max_tokens=max_tokens, temperature=temperature)

def _rrf_merge(bm25_hits: List[Dict], vec_hits: List[Dict], top_k: int = 6, k: float = 60.0) -> List[Dict]:
    pool: Dict[tuple, Dict] = {}
    for rank, h in enumerate(bm25_hits, 1):
        key = (h["title"], h["article"], h.get("clause"), h["source"])
        pool.setdefault(key, {"item": h.copy(), "rrf": 0.0, "bm_r": rank, "ve_r": 10**9})
        pool[key]["rrf"] += 1.0 / (k + rank)
    for rank, h in enumerate(vec_hits, 1):
        key = (h["title"], h["article"], h.get("clause"), h["source"])
        pool.setdefault(key, {"item": h.copy(), "rrf": 0.0, "bm_r": 10**9, "ve_r": rank})
        pool[key]["rrf"] += 1.0 / (k + rank)
        if "score" not in pool[key]["item"] and h.get("vscore") is not None:
            pool[key]["item"]["score"] = h["vscore"]
    merged = sorted(pool.values(), key=lambda x: (-x["rrf"], x["bm_r"], x["ve_r"]))
    out = []
    for x in merged[:top_k]:
        it = x["item"]
        it["rrf"] = round(x["rrf"], 6)
        out.append(it)
    return out

def load_index(data_dir: str) -> int:
    n = bm25_load_index(data_dir)
    if os.getenv("EMBEDDINGS_ENABLED", "true").lower() == "true":
        try:
            index_path = os.getenv("INDEX_PATH", "index/index.jsonl")
            m = load_vector_store(index_path)
            print(f"[vector] loaded {m} units from {index_path}")
        except Exception as e:
            print(f"[vector] skip: {e}")
    return n

def reload_index(data_dir: str) -> int:
    n = bm25_reload_index(data_dir)
    if os.getenv("EMBEDDINGS_ENABLED", "true").lower() == "true":
        try:
            index_path = os.getenv("INDEX_PATH", "index/index.jsonl")
            m = load_vector_store(index_path)
            print(f"[vector] reloaded {m} units from {index_path}")
        except Exception as e:
            print(f"[vector] skip reload: {e}")
    return n

def answer_question(question: str, settings: Settings) -> Dict:
    t_all = time.perf_counter()
    
    # Kiểm tra kết nối internet
    is_online = check_internet_connection()
    ai_type = "gemini" if is_online and os.getenv("GOOGLE_API_KEY", "").strip() else "ollama"
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash") if ai_type == "gemini" else os.getenv("LLM_MODEL", "qwen2.5:3b-instruct")
    
    # In thông tin trạng thái
    print_status_info(is_online, ai_type, model_name, question[:50], "")
    
    # Chọn titles
    print("🔍 Đang chọn phạm vi luật phù hợp...")
    t_title0 = time.perf_counter()
    chosen_titles = _pick_titles(question, settings.data_dir)
    t_title = (time.perf_counter() - t_title0) * 1000.0
    print_step_timing("Chọn phạm vi luật", t_title)
    
    # BM25 search
    print("📝 Đang tìm kiếm từ khóa (BM25)...")
    t_bm0 = time.perf_counter()
    bm = bm25_search(question, top_k=settings.top_k, allow_titles=chosen_titles or None)
    t_bm = (time.perf_counter() - t_bm0) * 1000.0
    print_step_timing("Tìm kiếm BM25", t_bm)

    # Vector search
    vc: List[Dict] = []
    t_vec = 0.0
    if os.getenv("EMBEDDINGS_ENABLED", "true").lower() == "true":
        print("🎯 Đang tìm kiếm ngữ nghĩa (Vector)...")
        t_v0 = time.perf_counter()
        try:
            vc = vector_search(
                question,
                top_k=settings.top_k,
                allow_titles=chosen_titles or None,
                embed_model=os.getenv("EMBED_MODEL", "nomic-embed-text"),
            )
        finally:
            t_vec = (time.perf_counter() - t_v0) * 1000.0
            print_step_timing("Tìm kiếm Vector", t_vec)

    # Merge results  
    print("🔄 Đang hợp nhất kết quả tìm kiếm...")
    t_merge0 = time.perf_counter()
    hits = _rrf_merge(bm, vc, top_k=settings.top_k)
    t_merge = (time.perf_counter() - t_merge0) * 1000.0
    print_step_timing("Hợp nhất kết quả", t_merge)
    # Format context
    print("📄 Đang định dạng ngữ cảnh...")
    t_ctx0 = time.perf_counter()
    ctx = _format_context(hits, settings.max_context_chars)
    t_ctx = (time.perf_counter() - t_ctx0) * 1000.0
    print_step_timing("Định dạng ngữ cảnh", t_ctx)
    
    # In thông tin context sau khi có
    if ctx:
        print_status_info(is_online, ai_type, model_name, question[:50], ctx[:50])

    # router direct-cite?
    direct_kw = re.compile(r"\b(điều\s+\d+|khoản\s+\d+|trích|khái\s*niệm|định\s*nghĩa|mức\s*phạt|xử\s*phạt|phạt)\b", re.I)
    use_direct = settings.direct_cite_first and (direct_kw.search(question) or not settings.llm_enabled)

    # Nếu không enable LLM hoặc không có context -> direct cite
    if use_direct or not ctx.strip() or not settings.llm_enabled:
        total = (time.perf_counter() - t_all) * 1000.0
        if not settings.llm_enabled:
            print("⚠️  LLM disabled - Chỉ trả về trích dẫn trực tiếp")
        else:
            print("✅ Sử dụng chế độ trích dẫn trực tiếp")
        out = _direct_cite(hits)
        
        timing_data = {
            "bm25_ms": round(t_bm, 2),
            "vector_ms": round(t_vec, 2),
            "llm_ms": 0.0,
            "total_ms": round(total, 2),
        }
        print_timing_info(timing_data)
        
        out.update({
            "chosen_titles": chosen_titles,
            "available_units": available_units(),
            "latency_ms": int(total),
            "timings": timing_data,
            "question_head": (question or "")[:50],
            "context_head": (ctx or "")[:50],
            "model": model_name,
            "ai": ai_type,
        })
        return out

    # LLM Processing
    print(f"🤖 Đang gửi yêu cầu đến AI ({ai_type.upper()})...")
    t_llm0 = time.perf_counter()
    content = _rag_answer(question, ctx, settings)
    t_llm = (time.perf_counter() - t_llm0) * 1000.0
    print_step_timing(f"Xử lý AI ({ai_type.upper()})", t_llm)
    
    total = (time.perf_counter() - t_all) * 1000.0
    
    timing_data = {
        "bm25_ms": round(t_bm, 2),
        "vector_ms": round(t_vec, 2),
        "llm_ms": round(t_llm, 2),
        "total_ms": round(total, 2),
    }
    print_timing_info(timing_data)

    return {
        "mode": "rag+llm",
        "answer": content,
        "citations": hits,
        "used_context": True,
        "chosen_titles": chosen_titles,
        "available_units": available_units(),
        "latency_ms": int(total),
        "timings": timing_data,
        "question_head": (question or "")[:50],
        "context_head": (ctx or "")[:50],
        "model": model_name,
        "ai": ai_type,
    }
