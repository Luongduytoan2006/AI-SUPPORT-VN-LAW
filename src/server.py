import os, time, requests
from pathlib import Path
from flask import Flask, send_from_directory, request, jsonify
import google.generativeai as genai

from core.pipeline import load_index, answer_question
from core.settings import Settings
from core.utils import print_status_info, print_step_timing, print_timing_info, check_internet_connection

ROOT = Path(__file__).resolve().parents[1]  # project root
APP_DIR = ROOT / "app"
GEMINI_PROMPT_PATH = ROOT / "prompts" / "gemini_answer.txt"

app = Flask(__name__, static_folder=str(APP_DIR), template_folder=str(APP_DIR))
app.secret_key = os.getenv('SECRET_KEY', 'vn-legal-assistant-2024')

settings = Settings()

# -----------------------------
# Helpers
# -----------------------------
def _online() -> bool:
    return check_internet_connection()

def _gemini_enabled() -> bool:
    return bool(os.getenv("GOOGLE_API_KEY", "").strip())

def _citations_to_context(citations) -> str:
    buf = []
    for c in citations or []:
        title  = c.get("title","")
        art    = c.get("article","")
        clause = c.get("clause")
        text   = (c.get("text") or "").strip()
        src    = c.get("source","")
        tag = f"[{title} | Điều {art}" + (f", Khoản {clause}]" if clause else "]")
        buf.append(f"{tag}\n{text}\nSOURCE: {src}")
    return "\n---\n".join(buf)

def _head(s: str, n: int = 50) -> str:
    s = (s or "").strip().replace("\n", " ")
    return s[:n]

def _gemini_answer(question: str, context: str) -> str | None:
    key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not key:
        return None
    model_id = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    genai.configure(api_key=key)
    
    # Đọc system prompt từ file
    try:
        system_prompt = GEMINI_PROMPT_PATH.read_text(encoding="utf-8")
    except Exception:
        # Fallback prompt nếu file không tồn tại
        system_prompt = (
            "Bạn là Luật sư tư vấn pháp luật Việt Nam chuyên nghiệp. "
            "Tư vấn dựa trên CONTEXT chính xác và thực tiễn. "
            "CHỈ sử dụng thông tin có trong CONTEXT. "
            "Mỗi kết luận phải có trích dẫn văn bản pháp luật đầy đủ (Luật/Nghị định | Điều X, Khoản Y). "
            "Trả lời đầy đủ, chi tiết như luật sư chuyên nghiệp."
        )
    
    prompt = f'''{system_prompt}

CONTEXT:
{context}

CÂU HỎI:
{question}
'''
    try:
        model = genai.GenerativeModel(model_id)
        res = model.generate_content(prompt)
        return (res.text or "").strip()
    except Exception:
        # Fallback: thử model 1.5 nếu 2.0 không khả dụng
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            res = model.generate_content(prompt)
            return (res.text or "").strip()
        except Exception as e2:
            print("Gemini error:", e2)
            return None

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    return send_from_directory(str(APP_DIR), "index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json() or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"status": "error", "error": "Vui lòng nhập câu hỏi"}), 400

    t_all0 = time.time()

    # ===== ONLINE BRANCH: Retrieval-only -> Gemini =====
    if _online() and _gemini_enabled():
        print("🌐 Sử dụng chế độ ONLINE với Gemini")
        print_status_info(True, "gemini", os.getenv("GEMINI_MODEL", "gemini-2.0-flash"), _head(question), "")
        
        # 1) Retrieval-only để lấy citations
        print("📚 Đang thực hiện retrieval...")
        t_ret0 = time.time()
        retrieval_only = Settings()
        retrieval_only.llm_enabled = False  # không gọi LLM Ollama
        rag = answer_question(question, settings=retrieval_only)
        t_ret_ms = round((time.time() - t_ret0) * 1000, 2)
        print_step_timing("Retrieval hoàn thành", t_ret_ms)

        citations = rag.get("citations", [])
        context = _citations_to_context(citations)

        # 2) Gọi Gemini
        print("🚀 Đang gửi yêu cầu đến Gemini...")
        t_llm0 = time.time()
        ans = _gemini_answer(question, context)
        t_llm_ms = round((time.time() - t_llm0) * 1000, 2)
        print_step_timing("Gemini xử lý", t_llm_ms)

        if ans:
            total_sec = round((time.time() - t_all0), 2)
            timing_data = {
                "retrieval_ms": t_ret_ms,
                "llm_ms": t_llm_ms,
                "total_ms": round(total_sec * 1000, 2),
            }
            print_timing_info(timing_data)
            
            return jsonify({
                "status": "success",
                "mode": "gemini-online",
                "answer": ans,
                "citations": citations,
                "latency_sec": total_sec,
                # META
                "ai": "gemini",
                "model": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
                "question_head": _head(question),
                "context_head": _head(context),
                "timings": timing_data,
            })

    # ===== OFFLINE BRANCH: Ollama pipeline (giữ nguyên logic) =====
    print("💻 Sử dụng chế độ OFFLINE với Ollama")
    t_pipe0 = time.time()
    rag = answer_question(question, settings=settings)
    t_total_ms = round((time.time() - t_pipe0) * 1000, 2)

    # cố gắng lấy context đầu nếu có
    citations = rag.get("citations", [])
    context = _citations_to_context(citations)
    
    # Sử dụng timing data từ pipeline nếu có
    timing_data = rag.get("timings", {
        "retrieval_ms": None,
        "llm_ms": None,
        "total_ms": t_total_ms,
    })

    return jsonify({
        "status": "success",
        "mode": "ollama-offline",
        "answer": rag.get("answer",""),
        "citations": citations,
        "latency_sec": round((time.time() - t_all0), 2),
        # META
        "ai": "ollama",
        "model": os.getenv("LLM_MODEL", "qwen2.5:3b-instruct"),
        "question_head": _head(question),
        "context_head": _head(context),
        "timings": timing_data,
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "internet": _online(),
        "gemini_configured": _gemini_enabled(),
        "ollama_configured": True,
        "timestamp": time.time()
    })

if __name__ == "__main__":
    print("🚀 Khởi động AURA Legal")
    print("📚 Loading index…")
    load_index(settings.data_dir)
    print("✅ Ready at http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)