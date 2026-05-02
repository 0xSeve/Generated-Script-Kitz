#!/usr/bin/env python3
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime
import os
import cgi
import sys
from common import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
LOG_FILE = os.path.join(BASE_DIR, "access.log")


class FullServeHandler(SimpleHTTPRequestHandler):

    def translate_path(self, path):
        path = path.split('?', 1)[0].split('#', 1)[0]
        path = os.path.normpath(path.lstrip('/'))
        full_path = os.path.join(BASE_DIR, path)

        if not os.path.realpath(full_path).startswith(os.path.realpath(BASE_DIR)):
            return BASE_DIR

        return full_path

    def log_access(self, code, size=0):
        ip = self.client_address[0]
        time_str = datetime.now().strftime('%d/%b/%Y:%H:%M:%S')
        log_line = f'{ip} - - [{time_str}] "{self.command} {self.path} {self.request_version}" {code} {size}\n'

        with open(LOG_FILE, "a") as f:
            f.write(log_line)

    # Disable directory listing completely
    def list_directory(self, path):
        self.send_error(403)
        self.log_access(403)
        return None

    def do_GET(self):
        # Normalize request path
        req_path = self.path.split('?', 1)[0].split('#', 1)[0]

        # Only allow /deploy/<file>
        if not req_path.startswith("/deploy/"):
            self.send_error(403)
            self.log_access(403)
            return

        # Resolve actual file path
        path = self.translate_path(req_path)

        # Must be a file inside deploy/
        deploy_dir = os.path.join(BASE_DIR, "deploy")

        if not os.path.realpath(path).startswith(os.path.realpath(deploy_dir)):
            self.send_error(403)
            self.log_access(403)
            return

        # Must exist and be a file
        if not os.path.isfile(path):
            self.send_error(403)
            self.log_access(403)
            return

        # Serve file
        super().do_GET()
        self.log_access(200)

    def send_error(self, code, message=None, explain=None):
        if code == 404:
            code = 403
            message = "Forbidden"

        super().send_error(code, message, explain)
        self.log_access(code)

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get('Content-Type', ''))

        if ctype != 'multipart/form-data':
            self.send_error(400)
            return

        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': self.headers['Content-Type']
            }
        )

        if 'file' not in form or not form['file'].filename:
            self.send_error(400)
            return

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        filename = os.path.basename(form['file'].filename)
        file_path = os.path.join(UPLOAD_DIR, filename)

        data = form['file'].file.read()

        with open(file_path, 'wb') as f:
            f.write(data)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"[+] Uploaded: {filename}\n".encode())

        self.log_access(200, size=len(data))


if __name__ == "__main__":
    # Pipe for parent <-> child communication
    r, w = os.pipe()

    pid = os.fork()
    if pid > 0:
        # Original parent
        os.close(w)
        daemon_pid = int(os.read(r, 32).decode())
        os.close(r)
        success("Create an alias to quickly terminate the server.")
        success(f"$ alias kill_server='kill {daemon_pid}'")
        os._exit(0)

    # First child
    os.close(r)
    os.setsid()

    pid2 = os.fork()
    if pid2 > 0:
        # First child exits after passing PID
        os.write(w, str(pid2).encode())
        os.close(w)
        os._exit(0)

    # Second child (actual daemon)
    os.close(w)

    # Redirect stdio to /dev/null
    sys.stdout.flush()
    sys.stderr.flush()

    with open('/dev/null', 'rb', 0) as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'ab', 0) as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())

    # Run server
    os.chdir(BASE_DIR)
    httpd = HTTPServer(("0.0.0.0", 8000), FullServeHandler)
    httpd.serve_forever()
