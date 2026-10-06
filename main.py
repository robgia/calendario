"""Punto di ingresso per l'APK (python-for-android, bootstrap webview): avvia Flask su localhost."""
from app import app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
