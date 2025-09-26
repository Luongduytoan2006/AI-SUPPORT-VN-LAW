# 🛠️ SETUP.md - Hướng dẫn Cài đặt AI Legal Assistant

> **Hướng dẫn chi tiết cài đặt hệ thống AI Legal Assistant từ A-Z**

## 📋 Yêu cầu hệ thống

### Tối thiểu
- **OS**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.10 hoặc cao hơn
- **RAM**: 8GB (khuyến nghị 16GB)
- **Ổ cứng**: 5GB trống
- **Internet**: Cần thiết cho việc cài đặt và sử dụng Gemini

### Khuyến nghị
- **CPU**: 4 cores trở lên
- **RAM**: 16GB trở lên
- **SSD**: Để tăng tốc độ vector search
- **GPU**: Không bắt buộc nhưng hữu ích cho Ollama

## 🚀 Cài đặt nhanh (5 phút)

```bash
# 1. Clone repository
git clone https://github.com/your-username/AI-Thuc-Chien.git
cd AI-Thuc-Chien

# 2. Tạo virtual environment
python -m venv venv

# 3. Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Cài đặt dependencies
pip install -r requirements.txt

# 5. Kiểm tra hệ thống
python check_system.py

# 6. Chạy server
python src/server.py
```

🎉 **Xong!** Truy cập http://localhost:5000

## 📦 Cài đặt chi tiết

### Bước 1: Chuẩn bị môi trường

#### 1.1. Cài đặt Python
```bash
# Kiểm tra Python version
python --version  # Cần >= 3.10

# Nếu chưa có Python 3.10+:
# Windows: Tải từ python.org
# macOS: brew install python@3.10
# Ubuntu: sudo apt install python3.10
```

#### 1.2. Clone repository
```bash
git clone https://github.com/your-username/AI-Thuc-Chien.git
cd AI-Thuc-Chien
```

### Bước 2: Thiết lập Python Environment

#### 2.1. Tạo virtual environment
```bash
python -m venv venv
```

#### 2.2. Kích hoạt environment
```bash
# Windows Command Prompt
venv\Scripts\activate

# Windows PowerShell  
venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

#### 2.3. Upgrade pip
```bash
python -m pip install --upgrade pip
```

### Bước 3: Cài đặt Dependencies

#### 3.1. Cài đặt requirements chính
```bash
pip install -r requirements.txt
```

#### 3.2. Verify cài đặt
```bash
pip list | grep -E "(flask|google|requests|rich|numpy|scikit-learn)"
```

### Bước 4: Cấu hình hệ thống

#### 4.1. Tạo file cấu hình (tùy chọn)
```bash
# Tạo file .env để cấu hình
echo "# AI Legal Assistant Configuration" > .env
echo "GOOGLE_API_KEY=your-gemini-api-key-here" >> .env
echo "LLM_MODEL=qwen2.5:3b-instruct" >> .env
echo "TOP_K=8" >> .env
echo "MAX_TOKENS=1000" >> .env
echo "EMBEDDINGS_ENABLED=true" >> .env
```

#### 4.2. Kiểm tra data
```bash
# Kiểm tra dữ liệu pháp luật
ls data/
# Phải thấy: hon_nhan.json, giao_thong_duong_bo.json, v.v.
```

### Bước 5: Cài đặt Ollama (Offline AI)

> **Lưu ý**: Bước này chỉ cần nếu bạn muốn sử dụng chế độ offline

#### 5.1. Cài đặt Ollama

**Windows:**
```bash
# Tải và cài đặt từ: https://ollama.ai/download/windows
# Hoặc sử dụng winget:
winget install Ollama.Ollama
```

**macOS:**
```bash
# Sử dụng Homebrew:
brew install ollama

# Hoặc tải từ: https://ollama.ai/download/mac
```

**Linux:**
```bash
# Cài đặt script:
curl -fsSL https://ollama.ai/install.sh | sh

# Hoặc manual:
# Tải binary từ https://ollama.ai/download/linux
```

#### 5.2. Khởi động Ollama service
```bash
# Windows/macOS: Ollama tự động chạy service
# Linux: 
sudo systemctl start ollama
sudo systemctl enable ollama
```

#### 5.3. Tải AI models
```bash
# Model chính cho text generation (bắt buộc)
ollama pull qwen2.5:3b-instruct

# Model cho embeddings (bắt buộc)
ollama pull nomic-embed-text

# Model phụ (tùy chọn)
ollama pull qwen2.5:7b-instruct  # Model lớn hơn, chất lượng cao hơn
```

#### 5.4. Kiểm tra Ollama
```bash
# Kiểm tra models đã tải
ollama list

# Test model
ollama run qwen2.5:3b-instruct "Xin chào"
```

### Bước 6: Cấu hình Gemini API (Online AI)

> **Lưu ý**: Bước này chỉ cần nếu bạn muốn sử dụng Gemini online

#### 6.1. Lấy Gemini API Key
1. Truy cập: https://makersuite.google.com/app/apikey
2. Đăng nhập Google account
3. Tạo API key mới
4. Copy API key

#### 6.2. Cấu hình API Key
```bash
# Cách 1: Environment variable (khuyến nghị)
export GOOGLE_API_KEY="your-actual-api-key-here"

# Cách 2: File .env
echo "GOOGLE_API_KEY=your-actual-api-key-here" >> .env

# Windows CMD:
set GOOGLE_API_KEY=your-actual-api-key-here
```

#### 6.3. Test Gemini API
```bash
python -c "
import os
import google.generativeai as genai
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('Hello')
print('Gemini OK:', response.text[:50])
"
```

### Bước 7: Build Vector Index

#### 7.1. Build index lần đầu
```bash
python src/tools/build_vector_index.py --data data --index index --batch-size 32
```

#### 7.2. Kiểm tra index
```bash
# Kiểm tra file index
ls -la index/
# Phải thấy: index.jsonl, meta.jsonl

# Kiểm tra kích thước
du -sh index/
```

### Bước 8: Kiểm tra hệ thống

#### 8.1. Chạy system check
```bash
python check_system.py
```

Kết quả mong đợi:
```
🔍 VN Legal Assistant - Kiểm tra hệ thống
============================================================

                     📊 Tổng quan hệ thống
╭───────────────────────────┬─────────────────┬────────────────╮
│ Thành phần                │ Trạng thái      │ Chi tiết       │
├───────────────────────────┼─────────────────┼────────────────┤
│ 🌐 Internet               │ ✅ Online       │ Kết nối OK     │
│ 🤖 Ollama                 │ ✅ OK           │ 3 models       │
│ 🧠 Gemini                 │ ✅ OK           │ API key OK     │
│ 📚 Dữ liệu                │ ✅ OK           │ 6 file JSON    │
│ 🎯 Vector Index           │ ✅ OK           │ 3197 entries   │
╰───────────────────────────┴─────────────────┴────────────────╯

✅ Hệ thống sẵn sàng hoạt động!
```

#### 8.2. Test CLI
```bash
python src/run_cli.py "Tuổi kết hôn tối thiểu ở Việt Nam là bao nhiêu?"
```

### Bước 9: Chạy hệ thống

#### 9.1. Khởi động web server
```bash
python src/server.py
```

#### 9.2. Truy cập web interface
Mở trình duyệt tại: http://localhost:5000

## 🔧 Cấu hình nâng cao

### Environment Variables

```bash
# File .env example
GOOGLE_API_KEY=your-gemini-api-key
LLM_MODEL=qwen2.5:3b-instruct
EMBED_MODEL=nomic-embed-text
GEMINI_MODEL=gemini-2.0-flash

# Search settings
TOP_K=8
MAX_CONTEXT_CHARS=6000
MAX_TOKENS=1000
TEMPERATURE=0.2

# Features
EMBEDDINGS_ENABLED=true
DIRECT_CITE_FIRST=false

# Ollama settings
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=ollama

# Data paths
DATA_DIR=data
INDEX_PATH=index/index.jsonl
```

### Port Configuration
```bash
# Đổi port server (mặc định: 5000)
python src/server.py --port 8080

# Hoặc set environment:
export PORT=8080
python src/server.py
```

### Production Settings
```bash
# Tắt debug mode
export FLASK_ENV=production

# Sử dụng Gunicorn (Linux/macOS)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.server:app
```

## 🚨 Xử lý sự cố

### Lỗi thường gặp

#### 1. "ModuleNotFoundError"
```bash
# Kiểm tra virtual environment đã activate chưa
which python  # Phải trỏ đến venv/bin/python

# Cài lại requirements
pip install -r requirements.txt --force-reinstall
```

#### 2. "Ollama connection failed"
```bash
# Kiểm tra Ollama service
curl http://localhost:11434/api/tags

# Restart Ollama
# Windows: Restart Ollama app
# macOS: brew services restart ollama  
# Linux: sudo systemctl restart ollama
```

#### 3. "Vector index not found"
```bash
# Rebuild index
python rebuild_index.py

# Hoặc manual build
python src/tools/build_vector_index.py
```

#### 4. "Gemini API error"
```bash
# Kiểm tra API key
echo $GOOGLE_API_KEY

# Test API key
curl -H "x-goog-api-key: $GOOGLE_API_KEY" \
  https://generativelanguage.googleapis.com/v1/models
```

#### 5. "Permission denied"
```bash
# Windows: Chạy PowerShell as Administrator
# macOS/Linux: 
chmod +x rebuild_index.py
chmod +x check_system.py
```

### Performance Issues

#### Chậm khi tìm kiếm
```bash
# Giảm TOP_K
export TOP_K=5

# Giảm MAX_CONTEXT_CHARS  
export MAX_CONTEXT_CHARS=4000

# Tắt vector search tạm thời
export EMBEDDINGS_ENABLED=false
```

#### Hết RAM
```bash
# Sử dụng model nhỏ hơn
ollama pull qwen2.5:1.5b-instruct
export LLM_MODEL=qwen2.5:1.5b-instruct

# Giảm batch size khi build index
python src/tools/build_vector_index.py --batch-size 16
```

## 📊 Monitoring & Logs

### Xem logs
```bash
# Chạy server với verbose logs
python src/server.py --debug

# Xem system logs
tail -f /var/log/ollama.log  # Linux
# Windows: Event Viewer > Applications
```

### Health check
```bash
# API health endpoint
curl http://localhost:5000/health

# System status
python check_system.py
```

## 🔄 Cập nhật hệ thống

### Cập nhật code
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Cập nhật models
```bash
ollama pull qwen2.5:3b-instruct
ollama pull nomic-embed-text
```

### Rebuild index (khi có data mới)
```bash
python rebuild_index.py
```

## 📞 Hỗ trợ

### Community
- **GitHub Issues**: Báo lỗi và thảo luận
- **Wiki**: Tài liệu chi tiết
- **Discussions**: Hỏi đáp cộng đồng

### Enterprise Support
- Email: support@ai-legal.vn  
- Hotline: 1900-xxxx
- Documentation: https://docs.ai-legal.vn

---

🎉 **Chúc mừng!** Bạn đã cài đặt thành công AI Legal Assistant.

Nếu gặp vấn đề, hãy kiểm tra lại từng bước hoặc tạo issue trên GitHub.