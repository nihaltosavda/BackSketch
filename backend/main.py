
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import time
import sys

# Fix import path
sys.path.append(str(Path(__file__).parent))

from utils import (
    remove_background,
    replace_background_color,
    validate_file_size,
    validate_mime_type,
    validate_image_bytes,
)

app = FastAPI()

# Allow all origins (for frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend folder
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# Helper Function
async def read_and_validate(file: UploadFile):
    # Check file type
    try:
        validate_mime_type(file.content_type or "")
    except:
        raise HTTPException(status_code=415, detail="Invalid file type")

    # Read file
    data = await file.read()

    # Check file size
    try:
        validate_file_size(data)
    except:
        raise HTTPException(status_code=413, detail="File too large")

    # Check image validity
    try:
        validate_image_bytes(data)
    except:
        raise HTTPException(status_code=422, detail="Invalid image")

    return data


# Routes

@app.get("/", response_class=HTMLResponse)
async def home():
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(str(index_file))


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    start = time.time()

    data = await read_and_validate(file)

    try:
        result = remove_background(data)
    except Exception:
        raise HTTPException(status_code=500, detail="Processing failed")

    print(f"Processed in {time.time() - start:.2f}s")

    filename = (file.filename or "image").split(".")[0] + "_nobg.png"

    return Response(
        content=result,
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/replace-bg")
async def replace_bg(
    file: UploadFile = File(...),
    color: str = Form("#ffffff"),
):
    start = time.time()

    data = await read_and_validate(file)

    # Simple color validation
    if not color.startswith("#") or len(color) not in [4, 7]:
        raise HTTPException(status_code=422, detail="Invalid color")

    try:
        result = replace_background_color(data, color)
    except Exception:
        raise HTTPException(status_code=500, detail="Processing failed")

    print(f"Processed in {time.time() - start:.2f}s")

    filename = (file.filename or "image").split(".")[0] + "_colorbg.png"

    return Response(
        content=result,
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )