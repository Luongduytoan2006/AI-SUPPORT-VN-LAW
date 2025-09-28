# 🏛️ AI Legal Assistant - Hệ thống Tư vấn Pháp luật Việt Nam# VN Legal Assistant (RAG + Gemini/Ollama)


> **Trợ lý thông minh hỗ trợ tư vấn pháp luật Việt Nam**  - **FE**: `app/index.html` (2 cột: nhập & trả lời, header/footer, loading indicator).

> Sử dụng công nghệ RAG (Retrieval-Augmented Generation) kết hợp AI để cung cấp thông tin pháp lý chính xác và thực tiễn.- **BE**: `src/server.py` (Flask). Router:

  - **Online** (có Internet + `GOOGLE_API_KEY`): chạy *retrieval only* ⇒ lấy citations ⇒ gọi **Gemini Flash** sinh câu trả lời.

## 🎯 Mục tiêu dự án  - **Offline**: gọi pipeline (Ollama) theo thiết kế gốc (BM25 + vector + RRF + LLM).

- **Prompts**: `prompts/final_answer.txt` cho offline.

AI Legal Assistant được xây dựng với sứ mệnh cao cả: **Hỗ trợ người dân Việt Nam tiếp cận thông tin pháp luật một cách dễ dàng, chính xác và miễn phí**.

## Chạy nhanh

### ✨ Tính năng chính```bash

python -m venv .venv

- 🔍 **Tìm kiếm thông minh**: Sử dụng BM25 + Vector search để tìm kiếm điều luật liên quansource .venv/bin/activate

- 🤖 **AI phân tích**: Gemini (online) hoặc Ollama (offline) để tạo câu trả lời chuyên nghiệp pip install -r requirements.txt

- 📚 **Trích dẫn chính xác**: Mỗi kết luận đều có trích dẫn điều, khoản cụ thểcp .env.example .env          # điền GOOGLE_API_KEY nếu dùng online

- 🌐 **Hoạt động đa chế độ**: Online với Gemini hoặc offline với Ollamapython src/server.py          # web

- 🔄 **Cập nhật linh hoạt**: Dễ dàng thêm/sửa dữ liệu luật pháp# hoặc: python src/run_cli.py "Câu hỏi thử"

- 📱 **Giao diện thân thiện**: Web interface đơn giản, dễ sử dụng```


### 🏗️ Kiến trúc hệ thống

```
User Question → Retrieval (BM25 + Vector) → AI Analysis → Structured Answer
     ↓              ↓                        ↓              ↓
   Input         Legal DB                  Gemini/       Markdown
              (JSON + Index)              Ollama        + Citations
```

## 📊 Dữ liệu pháp luật hiện có (nguồn chính: THƯ VIỆN PHÁP LUẬT)

- 🏠 **Hôn nhân và Gia đình**: Điều kiện kết hôn, ly hôn, tài sản chung
- 🚗 **Giao thông đường bộ**: Vi phạm, mức phạt, xử lý
- 🏢 **Lao động**: Hợp đồng, sa thải, quyền lợi người lao động  
- 🏡 **Đất đai**: Sử dụng đất, chuyển nhượng, tranh chấp
- 💡 **Sở hữu trí tuệ**: Bản quyền, nhãn hiệu, sáng chế
- 🔒 **An ninh mạng**: Bảo vệ dữ liệu, không gian mạng

## 🚀 Cách sử dụng

### 1. Cài đặt hệ thống
```bash
# Xem hướng dẫn chi tiết trong SETUP.md
```

### 2. Chạy web server (local)
```bash
python src/server.py
# Truy cập: http://localhost:5000
```

### 3. Sử dụng CLI test trước
```bash
python src/run_cli.py "Tôi có thể kết hôn ở tuổi nào?"
```

### 4. Build vector index (lần đầu chạy)
```bash
python rebuild_index.py
```

## 💡 Ví dụ câu hỏi

- "Tuổi kết hôn tối thiểu ở Việt Nam là bao nhiêu?"
- "Tôi bị sa thải không lý do, có được bồi thường không?"
- "Mức phạt vi phạm giao thông khi uống rượu bia là bao nhiêu?"
- "Quy trình đăng ký nhãn hiệu thương mại như thế nào?"
- "Tranh chấp đất đai được giải quyết ở đâu?"

## ⚙️ Cấu hình

Hệ thống tự động điều chỉnh theo môi trường:

- **🌐 Online**: Sử dụng Gemini API (cần GOOGLE_API_KEY)
- **💻 Offline**: Sử dụng Ollama local (tự động fallback)
- **🔄 Hybrid**: Kết hợp cả hai để tối ưu hiệu suất

### Thông số quan trọng

- `TOP_K=5`: Số kết quả tìm kiếm tối đa
- `MAX_CONTEXT_CHARS=3000`: Độ dài context cho AI
- `MAX_TOKENS=1000`: Độ dài câu trả lời
- `EMBEDDINGS_ENABLED=true`: Bật vector search

## 📁 Cấu trúc thư mục

```
AI-Thuc-Chien/
├── README.md              # File này - Giới thiệu dự án
├── SETUP.md               # Hướng dẫn cài đặt chi tiết
├── rebuild_index.py       # Script rebuild vector index
├── check_system.py        # Kiểm tra trạng thái hệ thống
├── requirements.txt       # Thư viện Python cần thiết
│
├── data/                  # Dữ liệu pháp luật (JSON)
│   ├── hon_nhan.json
│   ├── giao_thong_duong_bo.json
│   └── ...
│
├── index/                 # Vector embeddings
│   ├── index.jsonl        # Vector database
│   └── meta.jsonl         # Metadata
│
├── src/                   # Source code
│   ├── server.py          # Web server
│   ├── run_cli.py         # Command line interface
│   ├── core/              # Core modules
│   └── tools/             # Utility scripts
│
├── app/                   # Web frontend
│   └── index.html
│
└── prompts/               # AI prompts
    └── final_answer.txt   # Template câu trả lời
```

## 🛠️ Công nghệ sử dụng

- **🐍 Python 3.10+**: Ngôn ngữ chính
- **🔍 RAG Pipeline**: BM25 + FAISS Vector Search  
- **🤖 AI Models**: Google Gemini + Ollama
- **🌐 Web Framework**: Flask
- **📊 Data Format**: JSON + JSONL
- **💾 Vector DB**: FAISS + Custom JSONL

## 🎯 Lộ trình phát triển

### ✅ Đã hoàn thành
- [x] RAG pipeline cơ bản
- [x] Vector search với FAISS
- [x] Tích hợp Gemini + Ollama
- [x] Web interface
- [x] CLI tool
- [x] Rebuild index script

### 🔄 Đang phát triển
- [ ] Thêm dữ liệu luật mới
- [ ] Cải thiện độ chính xác
- [ ] Tối ưu hiệu suất
- [ ] Mobile-friendly UI

### 🚀 Tương lai
- [ ] Chat history
- [ ] User authentication
- [ ] API documentation
- [ ] Multi-language support
- [ ] Legal document parser

## 📞 Hỗ trợ

### 🐛 Báo lỗi
- Tạo issue trên GitHub
- Mô tả chi tiết lỗi và bước tái hiện
- Đính kèm log nếu có

### 💡 Góp ý
- Đề xuất tính năng mới
- Cải thiện dữ liệu pháp luật
- Tối ưu trải nghiệm người dùng

## ⚖️ Lưu ý pháp lý

> **Quan trọng**: Thông tin từ hệ thống chỉ mang tính tham khảo. 
> Để có tư vấn chính xác cho tình huống cụ thể, 
> vui lòng tham khảo luật sư hoặc cơ quan có thẩm quyền.

## 📄 Giấy phép

MIT License - Xem chi tiết trong file LICENSE

---

**🏛️ AI Legal Assistant** - *Công nghệ phục vụ công lý*

Made with ❤️ for Vietnamese legal community