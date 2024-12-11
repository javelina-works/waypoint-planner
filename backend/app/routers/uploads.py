# app/routers/uploads.py
from fastapi import APIRouter, File, UploadFile
import shutil
from pathlib import Path
from rio_tiler.io import Reader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = Path("./uploaded_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    logger.debug(f"File uploaded: {file.filename}")
    filepath = UPLOAD_DIR / file.filename
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with Reader(filepath) as cog:
        bounds = cog.bounds # (minx, miny, maxx, maxy)

    return {
        "filename": file.filename, 
        "url": f"/tiles/{file.filename}",
        "bounds": bounds,    
    }
