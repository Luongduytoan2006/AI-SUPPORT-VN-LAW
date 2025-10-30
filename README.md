# 🏛️ AURA Legal - Hệ thống Hỗ trợ Tra cứu Luật thông minh

> **Nền tảng AI hỗ trợ doanh nghiệp và tổ chức tra cứu văn bản pháp luật nội bộ**  
> Sử dụng công nghệ RAG (Retrieval-Augmented Generation) kết hợp AI để cung cấp câu trả lời chính xác dựa trên văn bản luật được cung cấp.

## 🎯 Mục tiêu dự án

AURA Legal được xây dựng để hỗ trợ **doanh nghiệp, công ty luật, tổ chức** có thể:
- 📚 **Đưa văn bản luật riêng** vào hệ thống (JSON format)
- 🔍 **Vector hóa tự động** các điều khoản pháp luật
- 🤖 **AI trả lời chính xác** hoàn toàn dựa trên văn bản được cung cấp
- ⚡ **Tra cứu nhanh** với BM25 + Vector Search
- 💡 **Không phụ thuộc internet** - có thể chạy offline với Ollama

## ✨ Tính năng chính

- 🔍 **Tìm kiếm thông minh**: BM25 + Vector search (FAISS/JSONL) để tìm kiếm điều luật liên quan
- 🤖 **AI phân tích**: Gemini (online) hoặc Ollama (offline) để tạo câu trả lời chuyên nghiệp
- 📚 **Trích dẫn chính xác**: Mỗi kết luận đều có trích dẫn điều, khoản cụ thể
- 🌐 **Hoạt động đa chế độ**: 
  - Online với Gemini (cần API key)
  - Offline với Ollama (không cần internet)
- 🔄 **Cập nhật linh hoạt**: Dễ dàng thêm/sửa dữ liệu luật pháp
- 📱 **Giao diện thân thiện**: Web interface đơn giản, dễ sử dụng

## 🏗️ Kiến trúc hệ thống

```
User Question → Retrieval (BM25 + Vector) → AI Analysis → Structured Answer
     ↓              ↓                        ↓              ↓
   Input      Legal Documents            Gemini/       Markdown
            (JSON + Index)              Ollama        + Citations
```

**Quy trình hoạt động:**
1. Người dùng đưa câu hỏi
2. Hệ thống tìm kiếm điều khoản liên quan (BM25 + Vector)
3. AI phân tích và trả lời dựa trên điều khoản tìm được
4. Trả về kết quả có cấu trúc với trích dẫn đầy đủ

## 📊 Dữ liệu mẫu hiện có

Dự án đi kèm với dữ liệu mẫu về pháp luật Việt Nam (nguồn: THƯ VIỆN PHÁP LUẬT):

- 🏠 **Hôn nhân và Gia đình**: Điều kiện kết hôn, ly hôn, tài sản chung
- 🚗 **Giao thông đường bộ**: Vi phạm, mức phạt, xử lý
- 🏢 **Lao động**: Hợp đồng, sa thải, quyền lợi người lao động  
- 🏡 **Đất đai**: Sử dụng đất, chuyển nhượng, tranh chấp
- 💡 **Sở hữu trí tuệ**: Bản quyền, nhãn hiệu, sáng chế
- 🔒 **An ninh mạng**: Bảo vệ dữ liệu, không gian mạng

**Lưu ý:** Bạn có thể xóa dữ liệu mẫu và thay bằng văn bản luật riêng của tổ chức.

## 🚀 Cách sử dụng

### 1. Cài đặt hệ thống
```bash
# Xem hướng dẫn chi tiết trong SETUP.md
python -m venv .venv
source .venv/bin/activate  # hoặc .venv\Scripts\activate trên Windows
pip install -r requirements.txt
cp .env.example .env       # điền GOOGLE_API_KEY nếu dùng online
```

### 2. Build vector index (lần đầu chạy)
```bash
python rebuild_index.py
```

### 3. Chạy web server
```bash
python src/server.py
# Truy cập: http://localhost:5000
```

### 4. Hoặc sử dụng CLI
```bash
python src/run_cli.py "Câu hỏi của bạn"
```

## 🔧 Cấu hình

Hệ thống tự động điều chỉnh theo môi trường:

- **🌐 Online**: Sử dụng Gemini API (cần GOOGLE_API_KEY trong .env)
- **💻 Offline**: Sử dụng Ollama local (tự động fallback)
- **🔄 Hybrid**: Kết hợp cả hai để tối ưu hiệu suất

### Thông số quan trọng (file .env)

```bash
# AI Provider
GOOGLE_API_KEY=your-key-here       # Nếu dùng Gemini online
GEMINI_MODEL=gemini-2.0-flash      # Model Gemini
LLM_MODEL=qwen2.5:3b-instruct      # Model Ollama offline
EMBED_MODEL=nomic-embed-text       # Model embedding

# Retrieval settings
TOP_K=5                            # Số kết quả tìm kiếm tối đa
MAX_CONTEXT_CHARS=3000             # Độ dài context cho AI
MAX_TOKENS=1000                    # Độ dài câu trả lời
EMBEDDINGS_ENABLED=true            # Bật vector search

# Data paths
DATA_DIR=data                      # Thư mục chứa file JSON luật
INDEX_PATH=index/index.jsonl       # File vector index
```

## 📁 Cấu trúc thư mục

```
AI-Thuc-Chien/
├── README.md                      # File này - Giới thiệu dự án
├── SETUP.md                       # Hướng dẫn cài đặt chi tiết
├── rebuild_index.py               # Script rebuild vector index
├── requirements.txt               # Thư viện Python cần thiết
│
├── data/                          # Dữ liệu pháp luật (JSON)
│   ├── hon_nhan.json              # Dữ liệu mẫu
│   ├── giao_thong_duong_bo.json   # Có thể thay bằng luật riêng
│   └── ...
│
├── index/                         # Vector embeddings (tự động tạo)
│   └── index.jsonl                # Vector database
│
├── src/                           # Source code (PRODUCTION)
│   ├── server.py                  # Web server Flask
│   ├── run_cli.py                 # Command line interface
│   │
│   ├── core/                      # Core modules
│   │   ├── pipeline.py            # RAG pipeline chính
│   │   ├── llm_client.py          # Ollama/OpenAI client
│   │   ├── settings.py            # Cấu hình
│   │   ├── utils.py               # Utilities
│   │   └── retrieval/             # Retrieval engines
│   │       ├── bm25_json.py       # BM25 search
│   │       ├── vector_jsonl.py    # Vector search JSONL
│   │       └── vector_faiss.py    # Vector search FAISS
│   │
│   └── tools/                     # Build tools
│       └── build_vector_index.py  # Vector index builder
│
├── tools/                         # Testing & utilities (không dùng production)
│   ├── check_system.py            # Kiểm tra hệ thống
│   └── test_system.py             # System tests
│
├── app/                           # Web frontend
│   └── index.html                 # Single-page application
│
└── prompts/                       # AI prompts (quan trọng!)
    ├── final_answer.txt           # Prompt cho Ollama (offline)
    └── gemini_answer.txt          # Prompt cho Gemini (online)
```

## 📝 Định dạng dữ liệu luật (JSON)

Để sử dụng dữ liệu luật riêng, tạo file JSON trong thư mục `data/` theo format:

```json
{
  "dieu_1": {
    "tiêu_đề": "Tên điều luật",
    "khoản": {
      "1": "Nội dung khoản 1",
      "2": {
        "điểm": {
          "a": "Nội dung điểm a",
          "b": "Nội dung điểm b"
        }
      }
    }
  },
  "dieu_2": {
    "tiêu_đề": "Điều khác",
    "toàn_văn": "Nội dung toàn văn (nếu không có khoản)"
  }
}
```

Sau khi thêm file mới, chạy:
```bash
python rebuild_index.py
```

## 🛠️ Công nghệ sử dụng

- **🐍 Python 3.10+**: Ngôn ngữ chính
- **🔍 RAG Pipeline**: BM25 + Vector Search (FAISS/JSONL)
- **🤖 AI Models**: 
  - Google Gemini Flash 2.0 (online)
  - Ollama - Qwen 2.5 3B (offline)
- **🌐 Web Framework**: Flask
- **📊 Data Format**: JSON (luật) + JSONL (vector index)
- **💾 Embedding**: nomic-embed-text via Ollama

## 💡 Ví dụ câu hỏi (với dữ liệu mẫu)

- "Tuổi kết hôn tối thiểu ở Việt Nam là bao nhiêu?"
- "Tôi bị sa thải không lý do, có được bồi thường không?"
- "Mức phạt vi phạm giao thông khi uống rượu bia là bao nhiêu?"
- "Quy trình đăng ký nhãn hiệu thương mại như thế nào?"
- "Tranh chấp đất đai được giải quyết ở đâu?"

## 🎯 Use Cases

### Công ty luật
- Tra cứu nhanh các điều khoản trong hợp đồng mẫu
- Tìm kiếm án lệ và quy định liên quan
- Hỗ trợ chuẩn bị tư liệu cho vụ việc

### Doanh nghiệp
- Kiểm tra tuân thủ pháp luật nội bộ
- Tra cứu quy định về lao động, thuế, bảo hiểm
- Tìm hiểu quy trình pháp lý cần thiết

### Tổ chức/Hiệp hội
- Cung cấp thông tin pháp luật cho thành viên
- Tư vấn tự động về quy định ngành
- Hỗ trợ đào tạo về pháp luật

## ⚠️ Lưu ý quan trọng

### ⚖️ Trách nhiệm pháp lý
> **Quan trọng**: Thông tin từ hệ thống chỉ mang tính tham khảo dựa trên dữ liệu được cung cấp. 
> Để có tư vấn chính xác cho tình huống cụ thể, vui lòng tham khảo luật sư hoặc cơ quan có thẩm quyền.

### � Bảo mật
- Không upload dữ liệu luật nhạy cảm lên internet
- Sử dụng chế độ offline với Ollama cho dữ liệu quan trọng
- Bảo vệ file .env và API keys

### 📊 Chất lượng dữ liệu
- Độ chính xác phụ thuộc vào chất lượng dữ liệu JSON đầu vào
- Cần cập nhật thường xuyên khi có văn bản mới
- Nên có quy trình kiểm tra kết quả AI

## 📞 Hỗ trợ & Đóng góp

### 🐛 Báo lỗi
- Tạo issue trên GitHub với mô tả chi tiết
- Đính kèm log và bước tái hiện lỗi
- Ghi rõ môi trường (OS, Python version)

### 💡 Đề xuất tính năng
- Mở discussion trên GitHub
- Giải thích use case cụ thể
- Đánh giá mức độ ưu tiên

### 🤝 Đóng góp code
- Fork repository
- Tạo branch cho feature/fix
- Submit pull request với mô tả rõ ràng

---

## 📝 Lịch sử phiên bản

### Version 1.0.0 (29/10/2025) - Refactored
**Thay đổi chính:**
- 🎯 Đổi mục tiêu: Từ "tư vấn pháp luật VN cho người dân" → "Hệ thống tra cứu luật cho doanh nghiệp/tổ chức"
- 📁 Tổ chức lại cấu trúc: Tách riêng `src/` (production) và `tools/` (utilities)
- 📝 Tập trung prompts: Tất cả prompts trong thư mục `prompts/`
  - Tạo `prompts/gemini_answer.txt` (Gemini online)
  - Cập nhật `prompts/final_answer.txt` (Ollama offline)
- 📚 Documentation đầy đủ: Thêm hướng dẫn chi tiết sử dụng dữ liệu riêng
- 🔧 Cải tiến trích dẫn: Hướng dẫn AI trích dẫn đúng tên văn bản (không dùng tên file)

**Features:**
- ✅ Hỗ trợ dữ liệu luật tùy chỉnh (JSON format)
- ✅ Chạy offline hoàn toàn với Ollama
- ✅ Online với Gemini API
- ✅ Vector search với BM25 + FAISS/JSONL
- ✅ Web interface + CLI

---

**Phát triển bởi**: AURA Legal Team  
**License**: MIT  
**Version**: 1.0.0

## 📄 Giấy phép

MIT License - Xem chi tiết trong file LICENSE

---

**🏛️ AURA Legal** - *AI-Unified Retrieval Assistant for Legal Documents*

Made with ❤️ in Vietnam