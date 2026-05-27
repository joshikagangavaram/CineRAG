import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

from rag_engine import RAGEngine


ROOT = Path(__file__).resolve().parents[1]
ENGINE = RAGEngine(ROOT / "data" / "tollywood_kb.json")


class ChatHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json(200, {"ok": True})

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            self._send_json(200, {"ok": True, "service": "tollywood-rag-chatbot"})
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/chat":
            self._send_json(404, {"error": "Not found"})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        question = str(payload.get("question", "")).strip()
        if not question:
            self._send_json(400, {"error": "Question is required"})
            return

        self._send_json(200, ENGINE.answer(question))


def run():
    host = "127.0.0.1"
    port = 8000
    server = HTTPServer((host, port), ChatHandler)
    print(f"Tollywood RAG backend running at http://{host}:{port}")
    print("Open frontend/index.html in your browser.")
    server.serve_forever()


if __name__ == "__main__":
    run()
