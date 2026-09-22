#!/usr/bin/env python3
import sys
from pathlib import Path

# Import your custom decoupled components
from HttpSocketHandler import ThreadedHandlerWithSockets
from ThreadedHttpServer import TimeoutThreadingHTTPServer

# Defaults: Port 8000
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class CustomFileServerHandler(ThreadedHandlerWithSockets):
    """
    Inherits your robust HTTP and WebSocket handler.
    Overrides log_message to ensure terminal output is readable.
    """

    def log_message(self, format, *args):
        sys.stderr.write(
            "%s - - [%s] %s\n"
            % (self.address_string(), self.log_date_time_string(), format % args)
        )


if __name__ == "__main__":
    print(f"Initializing Renier Barnard's TimeoutThreadingHTTPServer...", flush=True)

    # Initialize your custom server architecture
    server = TimeoutThreadingHTTPServer(
        server_address=("0.0.0.0", PORT),
        handler_class=CustomFileServerHandler,
        timeout_seconds=0,
    )

    print(f"Serving files from: {Path.cwd()}")
    print(f"Listening on http://0.0.0:{PORT} (Threaded)")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Shutdown signal received. Closing server sockets safely.")
        server.server_close()
