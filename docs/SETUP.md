# SETUP – VN Legal Assistant

## Yêu cầu
- Python 3.10+ (khuyến nghị 3.11)
- Ollama (đã pull model `qwen2.5:3b-instruct` + `nomic-embed-text`)
- (Tuỳ chọn) Google API Key để dùng Gemini online.

## Cài đặt
```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# chỉnh .env theo máy của bạn (OLLAMA_BASE_URL, LLM_MODEL, GOOGLE_API_KEY…)
```

## Chuẩn bị dữ liệu
- Đặt các file luật `.json` vào `./data/`
- (Nếu dùng vector_jsonl) build:
```bash
python src/tools/build_vector_index.py --data data --index index --batch-size 64 --resume
```

## Chạy BE test (không cần FE)
```bash
python src/run_cli.py "Camera trước cửa nhà có phải treo biển?"
```

## Chạy web app
```bash
python src/server.py
# mở http://localhost:5000
```
