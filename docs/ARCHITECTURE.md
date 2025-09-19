# Kiến trúc & Luồng xử lý

```
VN-LEGAL-ASSISTANT/
├─ app/                               # FE (tĩnh)
│  └─ index.html
├─ src/                               # BE (Flask) + core
│  ├─ server.py                       # Router online/offline
│  ├─ run_cli.py                      # Test nhanh BE
│  └─ core/
│     ├─ settings.py
│     ├─ pipeline.py
│     ├─ llm_client.py
│     ├─ utils.py
│     └─ retrieval/
│        ├─ bm25_json.py
│        ├─ vector_jsonl.py
│        └─ vector_faiss.py
├─ prompts/
│  └─ final_answer.txt
├─ data/   # (trống)   ─ bạn nạp sau
├─ index/  # (trống)   ─ bạn nạp sau
├─ docs/
└─ .env.example
```

## Luồng Online (có mạng + GOOGLE_API_KEY)
1) FE gửi `/ask`.
2) BE bật `Settings().llm_enabled = False` để **chỉ chạy retrieval** (BM25 + vector + RRF) ⇒ lấy **citations**.
3) Ghép citations thành **CONTEXT**.
4) Gọi **Gemini Flash** (mặc định `gemini-2.0-flash`) để sinh câu trả lời.
5) Trả về: `answer + citations + latency + mode=gemini-online`.

## Luồng Offline
1) FE gửi `/ask`.
2) BE gọi thẳng `pipeline.answer_question()` (Ollama) – giữ logic router direct‑cite/RAG+LLM.
3) Trả về: `answer + citations + latency + mode=ollama-offline`.

> Gốc tìm kiếm/nhúng/hợp nhất **không bị sửa** – chỉ bổ sung lớp router và sinh nội dung bằng Gemini khi online.
