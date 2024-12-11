# app/routers/uploads.py
from fastapi import APIRouter, File, UploadFile
import shutil
from pathlib import Path
from rio_tiler.io import Reader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

SERVER_ENV = "local"

UPLOAD_DIR = Path("uploaded_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    logger.debug(f"File uploaded: {file.filename}")
    filepath = UPLOAD_DIR / file.filename
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with Reader(filepath) as cog:
        bounds = cog.bounds # (minx, miny, maxx, maxy)

    # relative_path = f"./uploaded_images/{file.filename}"
    # file_path = filepath
    # file_path = filepath.absolute().as_posix()
    
    # Determine which URL to return
    if SERVER_ENV == "local":
        # file_path = str(filepath.absolute()).replace("\\", "/")
        file_path = filepath
        file_url = f"file://{file_path}"
    else:
        file_url = f"http://localhost:8000/uploaded_images/{file.filename}"


    return {
        "filename": file.filename, 
        "file_url": file_url,
        "bounds": bounds,    
    }
