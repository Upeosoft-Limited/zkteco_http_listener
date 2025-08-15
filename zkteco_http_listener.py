#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import threading
import requests
import sys

# --- CONFIG ---
LISTEN_PORT = 5000                      # Put this port into the device
LOG_FILE    = "zkteco_raw.log"          # Where to save raw lines
FORWARD_TO_ERP = True                   
ERP_URL     = "{ERP_API_SECRET}.cdata"


def append_log(line: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {line}\n")


class ZKHandler(BaseHTTPRequestHandler):
    # Silence default noisy logging
    def log_message(self, format, *args):
        return

    def _send_text(self, code: int, body: str):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_GET(self):

        if self.path.startswith("/iclock/getrequest"):
            print("📩 Got GETREQUEST from device")

        parsed = urlparse(self.path)
        if parsed.path == "/iclock/getrequest":
            # Device heartbeat / command poll
            qs = parse_qs(parsed.query or "")
            sn = (qs.get("SN", [""])[0]).strip()
            append_log(f"GET /iclock/getrequest SN={sn} from {self.client_address[0]}")
            self._send_text(200, "OK")
        else:
            self._send_text(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path.rstrip("/") == "/iclock/cdata":
            length = int(self.headers.get("Content-Length", "0") or 0)
            raw = self.rfile.read(length).decode("utf-8", errors="ignore")
            qs = parse_qs(parsed.query or "")
            sn = (qs.get("SN", [""])[0]).strip()

            # Log locally
            append_log(f"POST /iclock/cdata SN={sn} from {self.client_address[0]}\n{raw.rstrip()}")

            # Optionally forward to the ERP exactly like the device would
            if FORWARD_TO_ERP:
                try:
                    auth = (ERP_API_KEY, ERP_API_SECRET) if ERP_API_KEY else None
                    resp = requests.post(
                        ERP_URL,
                        params={"SN": sn} if sn else None,
                        data=raw,
                        timeout=15,
                        auth=auth,
                        headers={"Content-Type": "text/plain"}
                    )
                    append_log(f"Forwarded to the ERP -> {resp.status_code}")
                except Exception as e:
                    append_log(f"ERROR forwarding to the ERP: {e}")

            # Always acknowledge to the device
            self._send_text(200, "OK")
        else:
            self._send_text(404, "Not Found")


def run():
    server = HTTPServer(("0.0.0.0", LISTEN_PORT), ZKHandler)
    print(f"Listening on 0.0.0.0:{LISTEN_PORT} for /iclock/getrequest and /iclock/cdata …")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("\nServer stopped.")


if __name__ == "__main__":
    # Simple hint if the port is in use
    try:
        run()
    except OSError as e:
        print(f"Failed to bind port {LISTEN_PORT}: {e}\n"
              f"Tip: choose another LISTEN_PORT and update the device.")
        sys.exit(1)
