# PROMPTS

## final_answer.txt (offline/Ollama)
- Vai trò: Luật sư Việt Nam
- Quy tắc: không bịa – chỉ dùng CONTEXT; mọi kết luận phải có trích dẫn [title | Điều…, Khoản…].
- Định dạng: Kết luận nhanh → Phân tích theo chủ thể → Mức phạt → Căn cứ → Thiếu dữ liệu → Lưu ý.

## Gemini (online)
- Prompt cứng trong `src/server.py` (hàm `_gemini_answer`), vẫn theo triết lý: CHUẨN – RÕ – TRÍCH DẪN – NÊU THIẾU DỮ LIỆU.
- Có thể chỉnh model qua env `GEMINI_MODEL`, mặc định `gemini-2.0-flash` (fallback `gemini-1.5-flash`).
