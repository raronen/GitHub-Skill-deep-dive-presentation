#!/usr/bin/env python3
"""Serve one editable HTML deck and atomically save updates to that file."""

from __future__ import annotations

import argparse
import hmac
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


MAX_DECK_BYTES = 25 * 1024 * 1024


def overwrite_windows_shared(path: Path, temp_path: str) -> None:
    """Overwrite an open Windows file while allowing browser read sharing."""
    script = """
$source = [System.IO.File]::OpenRead($env:DECK_SAVE_SOURCE)
try {
    $target = [System.IO.File]::Open(
        $env:DECK_SAVE_TARGET,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::ReadWrite
    )
    try {
        $target.SetLength(0)
        $source.CopyTo($target)
        $target.Flush($true)
    } finally {
        $target.Dispose()
    }
} finally {
    $source.Dispose()
}
"""
    environment = os.environ.copy()
    environment["DECK_SAVE_SOURCE"] = temp_path
    environment["DECK_SAVE_TARGET"] = str(path)
    last_error = ""
    for attempt in range(5):
        if attempt:
            time.sleep(0.25 * attempt)
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )
        if result.returncode == 0:
            return
        last_error = (result.stderr or result.stdout).strip()
    raise OSError(last_error or "Windows shared-write fallback failed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--backup", type=Path)
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--token", required=True)
    return parser.parse_args()


def create_handler(
    deck_path: Path,
    backup_path: Path | None,
    token: str,
) -> type[BaseHTTPRequestHandler]:
    class DeckHandler(BaseHTTPRequestHandler):
        server_version = "DeckSaveServer/1.0"

        def log_message(self, _format: str, *_args: object) -> None:
            return

        def send_json(self, status: int, payload: dict[str, object]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def has_valid_token(self) -> bool:
            supplied = parse_qs(urlparse(self.path).query).get("token", [""])[0]
            return hmac.compare_digest(supplied, token)

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/" or not self.has_valid_token():
                self.send_json(404, {"error": "Not found."})
                return
            try:
                body = deck_path.read_bytes()
            except OSError as error:
                self.send_json(500, {"error": f"Could not read deck: {error}"})
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/save" or not self.has_valid_token():
                self.send_json(404, {"error": "Not found."})
                return
            try:
                content_length = int(self.headers.get("Content-Length", ""))
            except ValueError:
                self.send_json(411, {"error": "A valid Content-Length is required."})
                return
            if content_length <= 0 or content_length > MAX_DECK_BYTES:
                self.send_json(413, {"error": "Deck payload is empty or too large."})
                return

            body = self.rfile.read(content_length)
            try:
                html = body.decode("utf-8")
            except UnicodeDecodeError:
                self.send_json(400, {"error": "Deck must be UTF-8 HTML."})
                return
            lower_html = html.lower()
            required_markers = ("<!doctype html", 'id="deck-toolbar"', 'class="reveal"')
            if not all(marker in lower_html for marker in required_markers):
                self.send_json(400, {"error": "Payload is not a valid editable deck."})
                return

            temp_name: str | None = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="wb",
                    dir=deck_path.parent,
                    prefix=deck_path.name + ".",
                    suffix=".tmp",
                    delete=False,
                ) as temp_file:
                    temp_name = temp_file.name
                    temp_file.write(body)
                    temp_file.flush()
                    os.fsync(temp_file.fileno())
                try:
                    os.replace(temp_name, deck_path)
                    temp_name = None
                except PermissionError:
                    # OneDrive-backed files can deny atomic replacement while a
                    # browser has the destination open. The complete validated
                    # temporary copy still makes an in-place overwrite safe.
                    if os.name == "nt":
                        overwrite_windows_shared(deck_path, temp_name)
                    else:
                        with open(temp_name, "rb") as source, open(deck_path, "wb") as target:
                            while chunk := source.read(1024 * 1024):
                                target.write(chunk)
                            target.flush()
                            os.fsync(target.fileno())
                    os.unlink(temp_name)
                    temp_name = None
            except OSError as error:
                if temp_name:
                    try:
                        os.unlink(temp_name)
                    except OSError:
                        pass
                self.send_json(500, {"error": f"Could not save deck: {error}"})
                return

            if backup_path:
                backup_temp_name: str | None = None
                try:
                    with tempfile.NamedTemporaryFile(
                        mode="wb",
                        dir=backup_path.parent,
                        prefix=backup_path.name + ".",
                        suffix=".tmp",
                        delete=False,
                    ) as backup_temp_file:
                        backup_temp_name = backup_temp_file.name
                        backup_temp_file.write(body)
                        backup_temp_file.flush()
                        os.fsync(backup_temp_file.fileno())
                    os.replace(backup_temp_name, backup_path)
                    backup_temp_name = None
                except OSError as error:
                    if backup_temp_name:
                        try:
                            os.unlink(backup_temp_name)
                        except OSError:
                            pass
                    self.send_json(
                        500,
                        {"error": f"Deck saved, but backup failed: {error}"},
                    )
                    return

            self.send_json(
                200,
                {
                    "ok": True,
                    "saved": True,
                    "file": deck_path.name,
                    "fileName": deck_path.name,
                    "backup": backup_path.name if backup_path else None,
                },
            )

        def do_PUT(self) -> None:
            self.send_json(405, {"error": "Method not allowed."})

        def do_DELETE(self) -> None:
            self.send_json(405, {"error": "Method not allowed."})

    return DeckHandler


def main() -> None:
    args = parse_args()
    deck_path = args.file.expanduser().resolve(strict=True)
    if not deck_path.is_file() or deck_path.suffix.lower() not in {".html", ".htm"}:
        raise SystemExit("--file must point to an existing HTML file.")
    if not args.token:
        raise SystemExit("--token must not be empty.")
    backup_path = args.backup.expanduser().resolve() if args.backup else None
    if backup_path:
        if backup_path.suffix.lower() not in {".html", ".htm"}:
            raise SystemExit("--backup must point to an HTML file.")
        if not backup_path.parent.is_dir():
            raise SystemExit("--backup parent directory must exist.")
        if backup_path == deck_path:
            raise SystemExit("--backup must differ from --file.")
    server = ThreadingHTTPServer(
        ("127.0.0.1", args.port),
        create_handler(deck_path, backup_path, args.token),
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
