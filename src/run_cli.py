# run_cli.py
import os, sys
from core.settings import Settings
from core.pipeline import load_index, answer_question
from core.utils import print_timing_info

# pretty output
from rich.console import Console
from rich.table import Table
from rich import box  # để bảng nhìn gọn hơn

def _print_citations_table(cites, max_chars: int | None = None):
    if not cites:
        return
    console = Console()
    table = Table(
        title="Trích dẫn đã dùng",
        header_style="bold",
        box=box.SIMPLE_HEAVY,
        show_lines=False,
        expand=True,
    )
    table.add_column("Văn bản", style="cyan", no_wrap=True)
    table.add_column("Điều", justify="right", no_wrap=True)
    table.add_column("Khoản/điểm", justify="center", no_wrap=True)
    table.add_column("Score", justify="right", no_wrap=True)
    table.add_column("Nội dung", overflow="fold")

    for c in cites:
        sc = c.get("score")
        if sc is None:
            sc = c.get("vscore")
        sc_str = f"{float(sc):.4f}" if isinstance(sc, (int, float)) else "-"

        text = (c.get("text") or "").strip()
        if max_chars and max_chars > 0 and len(text) > max_chars:
            text = text[:max_chars] + " …"

        table.add_row(
            c.get("title", ""),
            str(c.get("article", "")),
            str(c.get("clause") or "-"),
            sc_str,
            text,
        )

    console.print(table)

def main():
    q = " ".join(sys.argv[1:]).strip()
    if not q:
        q = open("question/request.txt", "r", encoding="utf-8").read().strip()

    # load index
    print("=====[start] load index and embeddings…=====\n")
    settings = Settings()
    load_index(settings.data_dir)
    print("\n=====[done] index loaded.\n=====")

    # trả lời
    print("\n[start] SLM answering…")
    out = answer_question(q, settings=settings)
    print("\n===== [done] SLM answer =====")

    print("\n=== RESULT ===\n")
    max_chars_env = int(os.getenv("CITATION_MAX_CHARS", "0"))
    _print_citations_table(out.get("citations"), max_chars=None if max_chars_env <= 0 else max_chars_env)

    print("\n=== ANSWER ===\n")
    print(out.get("answer", ""))

    print("\n--- Meta ---")
    print("Mode:", out.get("mode"))
    print("AI:", out.get("ai", "unknown"))
    print("Model:", out.get("model", "unknown"))
    print("Chosen titles:", out.get("chosen_titles"))
    print("Latency:", f"{out.get('latency_ms','-')} ms")
    
    # In timing info nếu có
    if out.get("timings"):
        print("\n--- Timing Details ---")
        print_timing_info(out["timings"])

if __name__ == "__main__":
    main()
