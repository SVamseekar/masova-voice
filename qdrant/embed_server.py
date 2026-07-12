"""
Tiny local embedding server for n8n to call.
Wraps nomic-ai/nomic-embed-text-v1.5 via sentence-transformers.
Runs on http://localhost:17494
Start: python qdrant/embed_server.py
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from sentence_transformers import SentenceTransformer

MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"
QUERY_PREFIX = "search_query: "
PORT = 17494

print(f"Loading {MODEL_NAME} (downloads ~400MB on first run)...")
model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)
print(f"Model loaded. Listening on http://localhost:{PORT}")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/embed":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        text = body.get("text", "")

        vector = model.encode(QUERY_PREFIX + text).tolist()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"embedding": vector}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[embed] {args[0]} {args[1]}")


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
