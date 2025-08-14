# ZKTeco HTTP Listener & ERPNext Forwarder

A lightweight Python 3 HTTP server that listens for **ZKTeco biometric device pushes** (`/iclock/getrequest` and `/iclock/cdata`) and optionally **forwards the raw data** directly to an ERPNext endpoint.

This is ideal if your ZKTeco device **cannot reach ERPNext directly** (e.g., network segmentation, firewall) or if you want to **log all raw traffic** for debugging.

## Features

- **Receive GET & POST requests** from ZKTeco biometric devices
- **Logs all raw pushes** into a local file with timestamps
- **Configurable authentication** (API key/secret) for ERPNext
- **Simple to run** — no heavy dependencies

## Installation

### 1. Clone the repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

### Install required packages
pip install requests

## Configuration
LISTEN_PORT = 5000                      # Port to listen on (must match device config)
LOG_FILE    = "zkteco_raw.log"          # File where logs are stored
FORWARD_TO_ERP = True                   # True = Forward to ERPNext, False = Only log
ERP_URL     = "{YOUR_API_URL}.cdata"

## Usage
python3 zkteco_listener.py

### Expected output:
Listening on 0.0.0.0:5000 for /iclock/getrequest and /iclock/cdata …

### View logs
cat zkteco_raw.log

### Example Log Output
[2025-08-14 18:16:56] POST /iclock/cdata SN=SYZ8251201444 from 192.168.1.50
2   2025-08-14 18:16:56  0   1   0   0   0   255 0   0
Forwarded to ERPNext -> 200

### GET heartbeat request:
[2025-08-14 18:17:01] GET /iclock/getrequest SN=SYZ8251201444 from 192.168.1.50

## Troubleshooting
### Port already in use
Failed to bind port 5000: [Errno 98] Address already in use

### Solution
sudo lsof -i:5000
sudo kill <PID>

## Test with Curl
curl -X POST "{YOUR_API_URL}.cdata" \
     -H "Content-Type: text/plain" \
     --data-binary "sample raw data"

## Suppost
For questions or issues, open a GitHub Issue or email: karani@upeosoft.com
