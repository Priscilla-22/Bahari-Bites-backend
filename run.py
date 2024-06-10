# run.py
from server.app import create_app

if __name__ == "__main__":
    import os

    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
