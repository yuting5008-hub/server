from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time

state = {"cmd": "stop", "mode": 0, "intensity": 0, "updated_at": 0}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path == "/state":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(state).encode())
    def do_POST(self):
        if self.path == "/set":
            length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(length))
            state.update(data)
            state["updated_at"] = time.time()
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"ok")
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
