# app/routers/tiles.py
from fastapi import APIRouter, Query
from app.services.tiling_service import get_tile
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()

UPLOAD_DIR = Path("./uploaded_images")

@router.get("/tiles/{filename}/{z}/{x}/{y}.png")
def get_tile_endpoint(filename: str, z: int, x: int, y: int):
    # logger.debug("Did we get here?")
    image_path = UPLOAD_DIR / filename
    if not image_path.exists():
        logger.warning(f"File not found: {image_path}")
        return {"error": "File not found"}
    else: 
        logger.debug(f"File found: {image_path}")
    return get_tile(str(image_path), x, y, z)
