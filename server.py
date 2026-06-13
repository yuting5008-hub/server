from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
import urllib.request
import threading

state = {"cmd": "stop", "mode": 0, "intensity": 0, "updated_at": 0}
CLAUDE_KEY = "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"
history = []
count = 0

def ask_claude():
    global history, count
    count += 1
    if count == 1:
        msg = "開始控制玩具，送出第一個指令讓玩具動起來。"
    else:
        msg = "繼續控制玩具，根據節奏決定下一個指令。"
    history.append({"role":"user","content":msg})
    data = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 20,
        "system": "你是玩具遠端控制AI，正在控制用戶的玩具。每次必須送出一個指令讓玩具動。只能回覆以下其中一個，不能說其他話：set 1 1、set 2 2、set 3 3、set 4 4、set 5 5、stop",
        "messages": history
    }).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=data, method="POST")
    req.add_header("x-api-key", CLAUDE_KEY)
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("content-type", "application/json")
    res = urllib.request.urlopen(req)
    result = json.loads(res.read())
    reply = result["content"][0]["text"].strip()
    history.append({"role":"assistant","content":reply})
    return reply

def claude_loop():
    while True:
        try:
            reply = ask_claude()
            print(f"Claude指令：{reply}")
            parts = reply.split()
            if parts[0] == "stop":
                state.update({"cmd":"stop","mode":0,"intensity":0,"updated_at":time.time()})
            elif parts[0] == "set":
                state.update({"cmd":"set","mode":int(parts[1]),"intensity":int(parts[2]),"updated_at":time.time()})
        except Exception as e:
            print(f"錯誤：{e}")
        time.sleep(8)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path == "/state":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(state).encode())
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

t = threading.Thread(target=claude_loop, daemon=True)
t.start()
HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
