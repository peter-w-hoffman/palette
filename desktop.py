"""Run Palette as a standalone desktop app in a native macOS window.

Starts the FastAPI server in a background thread (unless one is already
running) and shows the app in a native WebKit window — no browser involved.
Closing the window stops the app.
"""
import os
import socket
import sys
import threading
import time

# Anchor to the project directory regardless of how we're launched (Finder
# launches apps with cwd="/", which would break template/DB resolution).
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
sys.path.insert(0, HERE)

LOG = "/tmp/palette-app.log"

HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}/"


def log(msg):
    with open(LOG, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def _port_open():
    try:
        with socket.create_connection((HOST, PORT), timeout=0.4):
            return True
    except OSError:
        return False


def _serve():
    try:
        import uvicorn
        from main import app
        uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
    except Exception as e:
        log(f"server error: {e!r}")


def _alert(message):
    try:
        import subprocess
        subprocess.run([
            "osascript", "-e",
            f'display dialog "{message}" buttons {{"OK"}} default button "OK" '
            f'with title "Palette" with icon caution',
        ], check=False)
    except Exception:
        pass


def main():
    log(f"launch; cwd={os.getcwd()}")
    if not _port_open():
        threading.Thread(target=_serve, daemon=True).start()
        for _ in range(50):  # wait up to ~10s for the server to come up
            if _port_open():
                break
            time.sleep(0.2)
    up = _port_open()
    log(f"server up={up}")

    # Don't show a blank window if the server never started — say what to do.
    if not up:
        _alert("Palette could not start its background server. "
               "Please run setup.command again. "
               "Technical details are in /tmp/palette-app.log")
        return

    try:
        import webview
        log("opening window")
        webview.create_window("Palette", URL, width=1200, height=820, min_size=(820, 560))
        webview.start()
        log("window closed")
    except Exception as e:
        log(f"webview error: {e!r}")
        raise


if __name__ == "__main__":
    main()
