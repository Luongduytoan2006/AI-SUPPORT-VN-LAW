# core/utils.py
import time, threading, requests
from contextlib import contextmanager
from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich import box
import datetime

class Heartbeat:
    def __init__(self, label: str = "Đang xử lý", every: float = 60.0):
        self.label = label
        self.every = max(1.0, float(every))
        self._stop = threading.Event()
        self._t = None

    def _run(self):
        elapsed = 0.0
        while not self._stop.wait(self.every):
            elapsed += self.every
            print(f"[⏳] {self.label}… {int(elapsed)}s", flush=True)

    def __enter__(self):
        self._t = threading.Thread(target=self._run, daemon=True)
        self._t.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._stop.set()
        if self._t and self._t.is_alive():
            self._t.join(timeout=0)

@contextmanager
def lap_timer(enabled: bool = True):
    t_last = time.perf_counter()
    def done(name: str):
        nonlocal t_last
        if not enabled:
            return
        now = time.perf_counter()
        dt = now - t_last
        t_last = now
        print(f"⏱️ {name}: {dt:.3f}s", flush=True)
    try:
        yield t_last, done
    finally:
        pass

def check_internet_connection(timeout: float = 3.0) -> bool:
    """Kiểm tra kết nối internet bằng cách ping Google."""
    try:
        response = requests.get("https://www.gstatic.com/generate_204", timeout=timeout)
        return response.status_code == 204
    except Exception:
        return False

def print_status_info(is_online: bool, ai_type: str, model: str, question_head: str, context_head: str):
    """In thông tin trạng thái và AI được sử dụng với giao diện đẹp."""
    console = Console()
    
    # Tạo bảng trạng thái
    status_table = Table(
        title="🤖 VN Legal Assistant - Thông tin phiên làm việc",
        header_style="bold blue",
        box=box.ROUNDED,
        show_header=True,
        expand=True
    )
    
    status_table.add_column("Thuộc tính", style="cyan", no_wrap=True, width=20)
    status_table.add_column("Giá trị", style="white")
    
    # Thời gian hiện tại
    current_time = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
    
    # Trạng thái kết nối
    connection_status = "🌐 ONLINE" if is_online else "💻 OFFLINE" 
    connection_color = "green" if is_online else "yellow"
    
    # AI type với màu sắc
    ai_display = f"🧠 {ai_type.upper()}" if ai_type else "❓ Unknown"
    ai_color = "green" if ai_type == "gemini" else "blue" if ai_type == "ollama" else "red"
    
    status_table.add_row("Thời gian", current_time)
    status_table.add_row("Trạng thái", Text(connection_status, style=connection_color))
    status_table.add_row("AI Engine", Text(ai_display, style=ai_color))
    status_table.add_row("Model", f"🎯 {model}")
    if question_head:
        status_table.add_row("Câu hỏi", f"❓ {question_head}...")
    if context_head:
        status_table.add_row("Context", f"📄 {context_head}...")
    
    console.print(status_table)
    console.print()

def print_timing_info(timing_data: dict):
    """In thông tin thời gian thực hiện với giao diện đẹp."""
    console = Console()
    
    timing_table = Table(
        title="⏱️ Thời gian xử lý chi tiết",
        header_style="bold magenta",
        box=box.SIMPLE_HEAVY,
        show_header=True
    )
    
    timing_table.add_column("Bước xử lý", style="cyan", no_wrap=True)
    timing_table.add_column("Thời gian (ms)", style="yellow", justify="right")
    timing_table.add_column("Ghi chú", style="white", overflow="fold")
    
    if "bm25_ms" in timing_data and timing_data["bm25_ms"] is not None:
        timing_table.add_row("🔍 BM25 Search", f"{timing_data['bm25_ms']:.2f}", "Tìm kiếm từ khóa")
    
    if "vector_ms" in timing_data and timing_data["vector_ms"] is not None:
        timing_table.add_row("🎯 Vector Search", f"{timing_data['vector_ms']:.2f}", "Tìm kiếm ngữ nghĩa")
        
    if "retrieval_ms" in timing_data and timing_data["retrieval_ms"] is not None:
        timing_table.add_row("📚 Retrieval", f"{timing_data['retrieval_ms']:.2f}", "Tổng thời gian truy xuất")
    
    if "llm_ms" in timing_data and timing_data["llm_ms"] is not None:
        timing_table.add_row("🤖 AI Processing", f"{timing_data['llm_ms']:.2f}", "Xử lý AI và sinh câu trả lời")
    
    if "total_ms" in timing_data:
        timing_table.add_row("⚡ Tổng cộng", f"{timing_data['total_ms']:.2f}", "Thời gian hoàn thành", style="bold green")
    
    console.print(timing_table)
    console.print()

def print_step_timing(step_name: str, duration_ms: float):
    """In thời gian thực hiện từng bước một cách đẹp mắt."""
    console = Console()
    
    # Tạo text với màu sắc tùy theo thời gian
    if duration_ms < 100:
        color = "green"
        icon = "⚡"
    elif duration_ms < 1000:
        color = "yellow" 
        icon = "⏱️"
    else:
        color = "red"
        icon = "🐌"
        
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    text = Text(f"[{timestamp}] {icon} {step_name}: {duration_ms:.2f}ms", style=color)
    console.print(text)
