# Python-Basic-File-Server

A lightweight, dependency-free HTTP file server built on Python's standard
library `http.server`. Serves files from the local filesystem, supports
WebSocket connections out of the box, and shuts itself down automatically
after a period of inactivity.

No third-party packages required — everything runs on the Python standard
library.

## Features

- **Static file serving** with automatic MIME type detection and gzip
  compression for small/medium files
- **Memory-efficient streaming** of large files — anything above the
  cacheable size threshold is streamed to the client in chunks rather than
  loaded fully into memory
- **Bounded, size-aware compression cache** — repeat requests for the same
  small file (HTML, CSS, JS, icons) are served from a compressed cache with
  an LRU eviction policy, so memory use stays capped
- **WebSocket support** built directly into the request handler (RFC 6455
  handshake, framing, ping/pong, masked frames), no external WebSocket
  library needed
- **Automatic inactivity shutdown** — the server can be configured to shut
  itself down after N seconds of no requests, useful for temporary/ad-hoc
  file sharing sessions
- **Threaded request handling** via `ThreadingHTTPServer`, so multiple
  clients can download or connect concurrently
- **Optional SSL/TLS support** via `SSLTimeoutThreadingServer`
- **JSON request/response helpers** for building small APIs alongside file
  serving
- **Basic security headers** (CSP, X-Frame-Options, X-Content-Type-Options,
  Referrer-Policy, Permissions-Policy) applied automatically to HTML
  responses

## Requirements

- Python 3.10+ (uses `match` statements and `X | Y` union type hints)
- No external dependencies

## Getting Started

Clone the repository and run the server from the directory you want to
serve:

```bash
git clone git@github.com:Ren-B-7/Python-Basic-File-Server.git
cd Python-Basic-File-Server
python3 main.py [port]
```

By default the server listens on port `8000`. To use a different port:

```bash
python3 main.py 9000
```

Then open `http://localhost:8000` (or your chosen port) in a browser.

## Project Structure

```
.
├── main.py            # Entry point — starts the server
├── server.py           # TimeoutThreadingHTTPServer / SSLTimeoutThreadingServer
├── handler.py           # Request handler: file serving, WebSockets, JSON helpers
├── icons/               # Static icon assets served via serve_icons()
└── utils/
    ├── __init__.py
    ├── constants.py     # Shared constants and the compression cache
    └── exceptions.py    # Custom exception types
```

## Configuration

Most behavior is controlled by constructor arguments and constants rather
than a config file:

| Setting                     | Where                                             | Default                  | Description                                                    |
| --------------------------- | ------------------------------------------------- | ------------------------ | -------------------------------------------------------------- |
| Port                        | CLI arg                                           | `8000`                   | Passed as `sys.argv[1]` to `main.py`                           |
| Inactivity timeout          | `TimeoutThreadingHTTPServer(timeout_seconds=...)` | `0` (disabled)           | Server shuts down after this many idle seconds                 |
| Max POST size               | `utils/constants.py` → `MAX_POST_SIZE`            | 64MB                     | Rejects larger POST bodies                                     |
| Max cacheable response size | `utils/constants.py` → `MAX_CACHEABLE_SIZE`       | 2MB                      | Files above this are streamed raw instead of compressed/cached |
| Compression cache size      | `utils/constants.py` → `COMPRESSION_CACHE`        | 128 entries / 32MB total | LRU-evicted cache of gzip output                               |

To enable an inactivity timeout, pass `timeout_seconds` when constructing
the server in `main.py`:

```python
server = TimeoutThreadingHTTPServer(
    server_address=('0.0.0.0', PORT),
    handler_class=CustomFileServerHandler,
    timeout_seconds=300,  # shuts down after 5 minutes idle
)
```

## Extending the Handler

`ThreadedHandlerWithSockets` is meant to be subclassed. Common extension
points:

- **`log_message`** — override to customize or redirect log output (see
  `CustomFileServerHandler` in `main.py`)
- **`on_ws_connected` / `on_ws_message` / `on_ws_closed`** — override to
  react to WebSocket lifecycle events
- **`do_GET` / `do_POST`** — implement your own routing on top of the
  provided `serve_file`, `serve_page`, `serve_icons`, `json_response`,
  `json_success`, and `json_error` helpers

Example minimal handler:

```python
from handler import ThreadedHandlerWithSockets
from pathlib import Path

class MyHandler(ThreadedHandlerWithSockets):
    def do_GET(self):
        if self.path == "/":
            self.serve_page("<h1>Hello, world</h1>")
        else:
            self.serve_file(Path(self.path.lstrip("/")))

    def on_ws_message(self, message):
        print("Received:", message)
        self.send_message(f"Echo: {message}")
```

## WebSocket Support

Connect to any path with a standard WebSocket handshake and the handler
will upgrade the connection automatically. Override `on_ws_message` in
your subclass to process incoming messages, and call `self.send_message(...)`
to send data back to the client.

## Security Notes

This project is intended for local/trusted-network file sharing (e.g. LAN
transfers, quick local previews) rather than as a public-facing production
server. Before exposing it beyond a trusted network, consider:

- Enabling `SSLTimeoutThreadingServer` with a valid certificate
- Adding authentication (none is built in)
- Reviewing the `Content-Security-Policy` in `send_headers_security()` for
  your use case
- Setting a sensible `MAX_POST_SIZE` and inactivity timeout for your
  environment

## License

MIT License

## Author

Renier Barnard — renier52147@gmail.com / renierb@axxess.co.za
