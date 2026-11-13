"""Local-only HTTP adapter. Start with python server.py; offline unless LESSON_LIVE=1."""
import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import threading
from app import execute

SLOTS = threading.BoundedSemaphore(2)


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, payload):
        body = json.dumps(payload).encode('utf8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.reply(200, {'status': 'healthy', 'service': 'lesson25'}) if self.path == '/health' else self.reply(404, {'error': 'not_found'})

    def do_POST(self):
        if self.path != '/ask':
            self.reply(404, {'error': 'not_found'})
            return
        if not SLOTS.acquire(blocking=False):
            self.reply(429, {'error': 'busy'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 1 <= length <= 4096:
                self.reply(413, {'error': 'body_must_be_1_to_4096_bytes'})
                return
            self.connection.settimeout(10)
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict) or not isinstance(data.get('question'), str):
                raise ValueError('question must be a string')
            report, folder = asyncio.run(execute(live=os.environ.get('LESSON_LIVE') == '1', data=data))
            self.reply(200, report)
        except (ValueError, TypeError):
            self.reply(400, {'error': 'invalid_request'})
        except Exception:
            self.reply(502, {'error': 'agent_run_failed'})
        finally:
            SLOTS.release()

    def log_message(self, format, *arguments):
        pass  # Do not log request bodies or credentials.


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 8000), Handler)
    print('Local exercise service: http://127.0.0.1:8000/health', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
