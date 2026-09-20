from fastapi import FastAPI


app = FastAPI(
    title="CurlyPots",
    description="CurlyPots Pottery Studio",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "CurlyPots API is running",
    }