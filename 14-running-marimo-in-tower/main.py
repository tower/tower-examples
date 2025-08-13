import os
from fastapi import FastAPI

import uvicorn 
import marimo

# Build the marimo ASGI app
server = (
    marimo.create_asgi_app()
        .with_app(path="/", root="./notebook.py")
)

# Mount into your FastAPI app
app = FastAPI()
app.mount("/", server.build())

def main():
    port = int(os.getenv("PORT", "50050"))
    hostname = os.getenv("TOWER__HOSTNAME", "(none)")
    print(f"Starting notebook for {hostname}")

    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            use_colors=False
        )
    except Exception as e:
        print(f"Failed to start server: {str(e)}")
        raise
    finally:
        print("FastAPI application shutting down...")
    
if __name__ == "__main__":
    main()
