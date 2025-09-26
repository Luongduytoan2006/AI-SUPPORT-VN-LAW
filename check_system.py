# -*- coding: utf-8 -*-
"""
Tool kiểm tra cấu hình và trạng thái hệ thống VN Legal Assistant
"""

import os
import sys
import requests
from pathlib import Path

# Thêm src vào path để import được
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.settings import Settings
from core.utils import check_internet_connection, print_status_info
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text
import datetime

def check_ollama_connection():
    """Kiểm tra kết nối đến Ollama"""
    try:
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        return False, str(e)

def check_gemini_config():
    """Kiểm tra cấu hình Gemini"""
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        return False, "Không có API Key"
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Test với một câu ngắn
        response = model.generate_content("Hello")
        return True, "Kết nối thành công"
    except Exception as e:
        return False, f"Lỗi: {e}"

def check_data_files():
    """Kiểm tra dữ liệu"""
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    if not data_dir.exists():
        return False, f"Thư mục {data_dir} không tồn tại"
    
    json_files = list(data_dir.glob("*.json"))
    if not json_files:
        return False, f"Không có file .json trong {data_dir}"
    
    return True, f"Có {len(json_files)} file dữ liệu: {[f.name for f in json_files[:3]]}..."

def check_index_files():
    """Kiểm tra index"""
    index_path = Path(os.getenv("INDEX_PATH", "index/index.jsonl"))
    if not index_path.exists():
        return False, f"File index {index_path} không tồn tại"
    
    file_size = index_path.stat().st_size
    return True, f"Index có kích thước {file_size // 1024}KB"

def main():
    console = Console()
    
    # Header
    console.print("🔍 VN Legal Assistant - Kiểm tra hệ thống", style="bold blue")
    console.print("=" * 60)
    console.print()
    
    # Load settings
    settings = Settings()
    
    # Tạo bảng trạng thái tổng quan
    status_table = Table(
        title="📊 Tổng quan hệ thống",
        header_style="bold green",
        box=box.ROUNDED,
        show_header=True,
        expand=True
    )
    
    status_table.add_column("Thành phần", style="cyan", no_wrap=True, width=25)
    status_table.add_column("Trạng thái", style="white", width=15)
    status_table.add_column("Chi tiết", style="white", overflow="fold")
    
    # Kiểm tra internet
    is_online = check_internet_connection()
    status_table.add_row(
        "🌐 Internet",
        Text("✅ Online" if is_online else "❌ Offline", style="green" if is_online else "red"),
        "Kết nối internet hoạt động" if is_online else "Không có kết nối internet"
    )
    
    # Kiểm tra Ollama
    ollama_ok, ollama_detail = check_ollama_connection()
    status_table.add_row(
        "🤖 Ollama",
        Text("✅ OK" if ollama_ok else "❌ Error", style="green" if ollama_ok else "red"),
        f"Ollama server: {settings.openai_base_url}" + (f" - {len(ollama_detail.get('models', []))} models" if ollama_ok and ollama_detail else f" - {ollama_detail}" if not ollama_ok else "")
    )
    
    # Kiểm tra Gemini
    gemini_ok, gemini_detail = check_gemini_config()
    status_table.add_row(
        "🧠 Gemini",
        Text("✅ OK" if gemini_ok else "❌ Error", style="green" if gemini_ok else "red"),
        f"Model: {os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')} - {gemini_detail}"
    )
    
    # Kiểm tra dữ liệu
    data_ok, data_detail = check_data_files()
    status_table.add_row(
        "📚 Dữ liệu",
        Text("✅ OK" if data_ok else "❌ Error", style="green" if data_ok else "red"),
        data_detail
    )
    
    # Kiểm tra index
    index_ok, index_detail = check_index_files()
    status_table.add_row(
        "🎯 Vector Index",
        Text("✅ OK" if index_ok else "❌ Error", style="green" if index_ok else "red"),
        index_detail
    )
    
    console.print(status_table)
    console.print()
    
    # Bảng cấu hình
    config_table = Table(
        title="⚙️ Cấu hình hiện tại",
        header_style="bold yellow",
        box=box.SIMPLE,
        show_header=True
    )
    
    config_table.add_column("Tham số", style="cyan", no_wrap=True)
    config_table.add_column("Giá trị", style="white")
    
    config_table.add_row("LLM Model", settings.llm_model)
    config_table.add_row("Embed Model", os.getenv("EMBED_MODEL", "nomic-embed-text"))
    config_table.add_row("Top K", str(settings.top_k))
    config_table.add_row("Max Context", str(settings.max_context_chars))
    config_table.add_row("Max Tokens", str(settings.max_tokens))
    config_table.add_row("Temperature", str(settings.temperature))
    config_table.add_row("Direct Cite First", str(settings.direct_cite_first))
    config_table.add_row("Embeddings Enabled", os.getenv("EMBEDDINGS_ENABLED", "true"))
    
    console.print(config_table)
    console.print()
    
    # Khuyến nghị
    recommendations = []
    
    if not is_online and not gemini_ok:
        recommendations.append("💡 Không có internet - hệ thống sẽ chỉ sử dụng Ollama offline")
    
    if not ollama_ok:
        recommendations.append("⚠️ Ollama không hoạt động - hãy khởi động Ollama trước")
    
    if not data_ok:
        recommendations.append("⚠️ Thiếu dữ liệu - hãy thêm file .json vào thư mục data/")
        
    if not index_ok and os.getenv("EMBEDDINGS_ENABLED", "true").lower() == "true":
        recommendations.append("⚠️ Thiếu vector index - chạy: python src/tools/build_vector_index.py")
    
    if recommendations:
        console.print("💡 Khuyến nghị:", style="bold yellow")
        for rec in recommendations:
            console.print(f"  {rec}")
    else:
        console.print("✅ Hệ thống sẵn sàng hoạt động!", style="bold green")
    
    console.print()
    console.print(f"Thời gian kiểm tra: {datetime.datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}")

if __name__ == "__main__":
    main()