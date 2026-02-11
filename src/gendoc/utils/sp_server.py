"""
Local HTTP server for SP selector HTML page.

Serves the HTML page and handles POST /save to write the JSON export
directly to the output directory — no browser download dialog needed.
"""

import http.server
import json
import threading
import webbrowser
from pathlib import Path

_server_instance = None
_server_lock = threading.Lock()


class _SPHandler(http.server.BaseHTTPRequestHandler):
    """Serves the SP selector HTML and saves exported JSON."""

    html_path: str = ""
    output_dir: str = ""

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(Path(self.html_path).read_bytes())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/save":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            out = Path(self.output_dir) / "sp_selection.json"
            out.write_bytes(body)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "path": str(out)
            }).encode("utf-8"))
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass  # silent


def start_sp_server(html_path: Path, output_dir: Path) -> dict:
    """
    Start a local HTTP server for the SP selector and open the browser.

    Args:
        html_path: Path to the generated HTML file
        output_dir: Directory where sp_selection.json will be saved

    Returns:
        Dict with url, port, output_dir
    """
    global _server_instance

    with _server_lock:
        # Stop previous server if running
        if _server_instance is not None:
            _server_instance.shutdown()
            _server_instance = None

        handler = type("Handler", (_SPHandler,), {
            "html_path": str(html_path),
            "output_dir": str(output_dir),
        })

        server = http.server.HTTPServer(("127.0.0.1", 0), handler)
        port = server.server_address[1]
        _server_instance = server

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    url = f"http://127.0.0.1:{port}/"
    webbrowser.open(url)

    return {"url": url, "port": port, "output_dir": str(output_dir)}


def stop_sp_server():
    """Stop the running SP selector server."""
    global _server_instance
    with _server_lock:
        if _server_instance is not None:
            _server_instance.shutdown()
            _server_instance = None
