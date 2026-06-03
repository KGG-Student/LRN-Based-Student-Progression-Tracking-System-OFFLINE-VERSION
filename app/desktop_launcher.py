import os
import socket
import threading
import time
import webbrowser
from pathlib import Path
from urllib.request import urlopen


def get_log_path():
    app_data_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "LRNTrackingSystem"
    app_data_dir.mkdir(parents=True, exist_ok=True)
    return app_data_dir / "launcher.log"


def write_log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with get_log_path().open("a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def configure_standalone_environment():
    os.environ.setdefault("APP_DB_ENGINE", "sqlite")
    os.environ.setdefault("FLASK_SECRET_KEY", "standalone-local-secret")


def run_flask_app(port):
    try:
        from app import app

        app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)
    except Exception as error:
        write_log(f"Flask startup failed: {error!r}")
        raise


def wait_for_app(url, timeout_seconds=30):
    deadline = time.time() + timeout_seconds
    login_url = f"{url}/login"
    last_error = None

    while time.time() < deadline:
        try:
            with urlopen(login_url, timeout=2) as response:
                if response.status < 500:
                    return True
        except Exception as error:
            last_error = error
            time.sleep(0.5)

    write_log(f"Timed out waiting for {login_url}: {last_error!r}")
    return False


def main():
    configure_standalone_environment()
    port = int(os.environ.get("LRN_STANDALONE_PORT") or find_free_port())
    url = f"http://127.0.0.1:{port}"
    write_log(f"Starting LRN Tracking System at {url}")

    server_thread = threading.Thread(target=run_flask_app, args=(port,), daemon=True)
    server_thread.start()
    is_ready = wait_for_app(url)

    if os.environ.get("LRN_STANDALONE_HEADLESS") == "1":
        server_thread.join()
        return

    if not is_ready:
        webbrowser.open(url)
        server_thread.join()
        return

    try:
        import webview

        webview.create_window("LRN Tracking System", url, width=1280, height=820)
        webview.start(gui="edgechromium")
    except Exception as error:
        write_log(f"Embedded WebView failed, opening browser fallback: {error!r}")
        webbrowser.open(url)
        server_thread.join()


if __name__ == "__main__":
    main()
