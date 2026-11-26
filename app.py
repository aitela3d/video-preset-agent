"""Web UI server: python3 app.py, then open http://localhost:8000

GET /                 -> static/index.html
GET /api/run?idea=..&model=auto|seedance|kling|wan -> live agent steps as Server-Sent Events
GET /api/runs         -> list of saved runs (for Replay)
GET /api/runs/<file>  -> one saved run (Replay plays its events without calling the API)
"""
import json, os, re, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from agent import ROOT, TARGETS, AgentError, run_agent, save_run

PORT = 8000
RUNS = os.path.join(ROOT, "runs")


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            with open(os.path.join(ROOT, "static", "index.html"), "rb") as f:
                return self.send(200, f.read(), "text/html")
        if url.path == "/api/runs":
            return self.send(200, list_runs())
        m = re.fullmatch(r"/api/runs/([\w-]+\.json)", url.path)
        if m and os.path.exists(os.path.join(RUNS, m.group(1))):
            with open(os.path.join(RUNS, m.group(1)), "rb") as f:
                return self.send(200, f.read())
        if url.path == "/api/run":
            q = parse_qs(url.query)
            return self.stream_run(q.get("idea", [""])[0].strip()[:300], q.get("model", ["auto"])[0])
        self.send(404, {"error": "not found"})

    def stream_run(self, idea, choice):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        alive = [True]

        def event(name, data):
            if not alive[0]:
                return
            try:
                self.wfile.write(("event: %s\ndata: %s\n\n" % (name, json.dumps(data, ensure_ascii=False))).encode())
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                alive[0] = False  # browser closed the tab; the run still finishes and is saved

        if not idea:
            return event("error", {"message": "Please enter an idea."})
        try:
            run = run_agent(idea, choice if choice in TARGETS else "auto", lambda s, d: event("step", {"step": s, **d}))
            event("saved", {"file": save_run(run)})
        except AgentError as e:
            event("error", {"message": str(e)})
        except Exception as e:  # never leak a traceback to the page, keep a short message
            event("error", {"message": "Unexpected error: %s" % type(e).__name__})
            print("Run failed:", repr(e), file=sys.stderr)

    def log_message(self, fmt, *args):  # quiet console: only errors
        if args and str(args[1]).startswith(("4", "5")):
            sys.stderr.write("%s\n" % (fmt % args))


def list_runs():
    out = []
    for name in sorted(os.listdir(RUNS), reverse=True) if os.path.isdir(RUNS) else []:
        if name.endswith(".json"):
            try:
                with open(os.path.join(RUNS, name)) as f:
                    fin = json.load(f)["final"]
                out.append({"file": name, "idea": fin["idea"], "name": fin["name"],
                            "first": fin["first_score"], "final": fin["final_score"]})
            except (ValueError, KeyError):
                continue
    return out


if __name__ == "__main__":
    print("Video Preset Agent running at http://localhost:%d  (Ctrl+C to stop)" % PORT)
    try:
        ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        pass
