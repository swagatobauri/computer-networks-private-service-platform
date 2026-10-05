from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, send_body=True):
        body = json.dumps(data).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "public, max-age=60")
        self.send_header("ETag", '"backend-b-v1"')
        self.send_header("X-Backend", "B")
        self.end_headers()

        if send_body:
            self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self.send_json({
                "message": "Hello from Backend B",
                "backend": "B"
            })

        elif self.path == "/api/status":
            self.send_json({
                "status": "ok",
                "backend": "B"
            })

        else:
            self.send_response(404)
            self.end_headers()

    def do_HEAD(self):
        if self.path in ["/", "/api/status"]:
            if self.path == "/":
                data = {
                    "message": "Hello from Backend B",
                    "backend": "B"
                }
            else:
                data = {
                    "status": "ok",
                    "backend": "B"
                }

            self.send_json(data, send_body=False)

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print("[Backend B]", format % args)

server = HTTPServer(("0.0.0.0", 3002), Handler)

print("Backend B running on http://0.0.0.0:3002")

server.serve_forever()
