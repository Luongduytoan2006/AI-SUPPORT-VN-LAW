# VN Legal Assistant (RAG + Gemini/Ollama)

- **FE**: `app/index.html` (2 cột: nhập & trả lời, header/footer, loading indicator).
- **BE**: `src/server.py` (Flask). Router:
  - **Online** (có Internet + `GOOGLE_API_KEY`): chạy *retrieval only* ⇒ lấy citations ⇒ gọi **Gemini Flash** sinh câu trả lời.
  - **Offline**: gọi pipeline (Ollama) theo thiết kế gốc (BM25 + vector + RRF + LLM).
- **Prompts**: `prompts/final_answer.txt` cho offline.

## Chạy nhanh
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # điền GOOGLE_API_KEY nếu dùng online
python src/server.py          # web
# hoặc: python src/run_cli.py "Câu hỏi thử"
```
