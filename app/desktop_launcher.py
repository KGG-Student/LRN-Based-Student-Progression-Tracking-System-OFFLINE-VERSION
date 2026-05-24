import os
import socket
import threading
import time
import webbrowser


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def configure_standalone_environment():
    os.environ.setdefault("APP_DB_ENGINE", "sqlite")
    os.environ.setdefault("FLASK_SECRET_KEY", "standalone-local-secret")


def run_flask_app(port):
    from app import app

    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


def main():
    configure_standalone_environment()
    port = int(os.environ.get("LRN_STANDALONE_PORT") or find_free_port())
    url = f"http://127.0.0.1:{port}"

    server_thread = threading.Thread(target=run_flask_app, args=(port,), daemon=True)
    server_thread.start()
    time.sleep(1)

    if os.environ.get("LRN_STANDALONE_HEADLESS") == "1":
        server_thread.join()
        return

    try:
        import webview

        webview.create_window("LRN Tracking System", url, width=1280, height=820)
        webview.start()
    except Exception:
        webbrowser.open(url)
        server_thread.join()


if __name__ == "__main__":
    main()
