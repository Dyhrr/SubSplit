import threading
import webview
import uvicorn
from src.api import app

def start_api():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    # Start the FastAPI backend in a separate thread
    threading.Thread(target=start_api, daemon=True).start()

    # Launch the frontend using pywebview
    webview.create_window("SubSplit", "http://127.0.0.1:8000/ui")
    webview.start()
