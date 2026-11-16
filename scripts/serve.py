"""serve.py: serve a directory with automatic free port detection.

Usage:
    python3 scripts/serve.py [_site] [--port 8765] [--print-port-only]

Finds an available port starting at 8765 (or --port). If the port is already
occupied, advances to the next free port and reports the chosen address.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import pathlib
import socket
import sys


def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a port is available for binding."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def find_free_port(start_port: int = 8765, max_attempts: int = 100, host: str = "127.0.0.1") -> int:
    """Find the first free port starting at start_port."""
    for p in range(start_port, start_port + max_attempts):
        if is_port_available(p, host):
            return p
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return sock.getsockname()[1]


def run_server(directory: pathlib.Path, port: int, host: str = "127.0.0.1") -> None:
    """Run HTTP server serving directory."""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    with http.server.ThreadingHTTPServer((host, port), handler) as httpd:
        print(f"Serving {directory} at http://localhost:{port}/ (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "directory",
        nargs="?",
        default="_site" if pathlib.Path("_site").is_dir() else ".",
        help="Directory to serve (default: _site if present, else .)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Preferred starting port (default: 8765)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface to bind (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--print-port-only",
        action="store_true",
        help="Print the resolved port and exit immediately",
    )
    args = parser.parse_args(argv)

    target_dir = pathlib.Path(args.directory).resolve()
    if not target_dir.is_dir():
        print(f"Error: directory not found: {target_dir}", file=sys.stderr)
        return 1

    resolved_port = find_free_port(args.port, host=args.host)
    if resolved_port != args.port and not args.print_port_only:
        print(f"Port {args.port} is in use. Using free port {resolved_port}.")

    if args.print_port_only:
        print(resolved_port)
        return 0

    run_server(target_dir, resolved_port, host=args.host)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
