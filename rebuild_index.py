# -*- coding: utf-8 -*-
"""
Script to build vector index (only if not exists)
"""
import os
import sys
from pathlib import Path

# Add src to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

def main():
    """Build vector index (skip if already exists)"""
    print("🔄 AI Legal Assistant - Build Vector Index")
    print("=" * 50)
    
    # Paths
    index_dir = ROOT / "index"
    data_dir = ROOT / "data"
    index_file = index_dir / "index.jsonl"
    
    if not data_dir.exists():
        print(f"❌ Data directory {data_dir} không tồn tại!")
        return 1
    
    # Check if index already exists
    if index_file.exists():
        file_size = index_file.stat().st_size // 1024
        with open(index_file, 'r', encoding='utf-8') as f:
            lines = sum(1 for _ in f)
        print(f"✅ Vector index đã tồn tại:")
        print(f"   - File: {index_file}")
        print(f"   - Entries: {lines:,}")
        print(f"   - Size: {file_size:,} KB")
        print("💡 Sử dụng index hiện có. Nếu muốn rebuild, xóa thư mục index/ trước.")
        return 0
        
    # Create index directory if not exists
    index_dir.mkdir(exist_ok=True)
    print(f"📁 Tạo thư mục index: {index_dir}")
    
    # Run the build script
    print("🚀 Bắt đầu build vector index...")
    build_script = ROOT / "src" / "tools" / "build_vector_index.py"
    
    cmd = f'python "{build_script}" --data "{data_dir}" --index "{index_dir}" --batch-size 32'
    print(f"⚡ Executing: {cmd}")
    
    result = os.system(cmd)
    
    if result == 0:
        print("✅ Build vector index thành công!")
        
        # Show index stats
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                lines = sum(1 for _ in f)
            file_size = index_file.stat().st_size // 1024
            print(f"📊 Index stats:")
            print(f"   - Entries: {lines:,}")
            print(f"   - Size: {file_size:,} KB")
        
        print("💡 Khuyến nghị:")
        print("   - Đảm bảo EMBEDDINGS_ENABLED=true trong .env")
        print("   - Restart server để load index mới")
        
        return 0
    else:
        print("❌ Build vector index thất bại!")
        return 1

if __name__ == "__main__":
    sys.exit(main())