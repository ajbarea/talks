"""Tests for serve.py free-port detection and build.py template guard (#130)."""

from __future__ import annotations

import pathlib
import socket
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SERVE_PY = ROOT / "scripts" / "serve.py"
BUILD_PY = ROOT / "aware-ai-midpoint-2027" / "build.py"


def test_find_free_port_when_occupied() -> None:
    # Import find_free_port and is_port_available directly
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import serve

        # Hold a socket on an ephemeral port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as occupied:
            occupied.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            occupied.bind(("127.0.0.1", 0))
            occupied.listen(1)
            port = occupied.getsockname()[1]

            # Verify it reports as unavailable
            assert not serve.is_port_available(port)

            # Requesting start_port=port should pick a different (available) port
            free_port = serve.find_free_port(start_port=port, max_attempts=5)
            assert free_port != port
            assert serve.is_port_available(free_port)
    finally:
        sys.path.pop(0)


def test_serve_cli_print_port_only() -> None:
    res = subprocess.run(
        [sys.executable, str(SERVE_PY), "--print-port-only", "--port", "9870"],
        capture_output=True,
        text=True,
        check=True,
    )
    port_str = res.stdout.strip()
    assert port_str.isdigit()
    port = int(port_str)
    assert port >= 9870


def test_serve_cli_missing_directory(tmp_path: pathlib.Path) -> None:
    nonexistent = tmp_path / "does-not-exist"
    res = subprocess.run(
        [sys.executable, str(SERVE_PY), str(nonexistent)],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 1
    assert "directory not found" in res.stderr


def test_aware_ai_build_missing_template(tmp_path: pathlib.Path) -> None:
    nonexistent_template = tmp_path / "missing-symposium.pptx"
    out_dir = tmp_path / "out"
    res = subprocess.run(
        [sys.executable, str(BUILD_PY), str(nonexistent_template), str(out_dir)],
        capture_output=True,
        text=True,
    )
    assert res.returncode != 0
    assert "template not found" in res.stderr or "template not found" in res.stdout
    assert "AWARE-AI cohort symposium template" in (res.stderr + res.stdout)
