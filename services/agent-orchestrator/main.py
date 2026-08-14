from app.server import app  # noqa: F401  (uvicorn entrypoint: main:app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
