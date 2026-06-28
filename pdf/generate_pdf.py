import functools
import http.server
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT / "pdf"


def pdf_path(level: str) -> Path:
    return PDF_DIR / f"kanji-{level}.pdf"


def _start_server(port: int) -> http.server.ThreadingHTTPServer:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def render(level: str, port: int) -> Path:
    from playwright.sync_api import sync_playwright

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    out = pdf_path(level)
    url = f"http://127.0.0.1:{port}/print.html?level={level}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_function("window.__renderComplete === true", timeout=30000)
        page.pdf(path=str(out), format="A4", print_background=True,
                 margin={"top": "14mm", "bottom": "14mm", "left": "14mm", "right": "14mm"})
        browser.close()
    print(f"Wrote {out}")
    return out


def main() -> None:
    port = 8123
    httpd = _start_server(port)
    try:
        for level in ("N5", "N4", "N3", "N2"):
            render(level, port)
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    main()
