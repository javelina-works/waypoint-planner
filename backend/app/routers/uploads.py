# app/routers/uploads.py
from fastapi import APIRouter, File, UploadFile, HTTPException
import shutil
from pathlib import Path
# from rio_tiler.io import Reader
# from pyproj import Transformer
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

SERVER_ENV = "local"
SET_CRS = "EPSG:3857" # Web Mercator

UPLOAD_DIR = Path("uploaded_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    logger.debug(f"File uploaded: {file.filename}")
    filepath = UPLOAD_DIR / file.filename
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with rasterio.open(filepath) as src:
        bounds = src.bounds # (minx, miny, maxx, maxy)

        if src.crs != SET_CRS:
            logger.debug("Reprojecting image!")
            output_filepath = UPLOAD_DIR / f"reprojected_{file.filename}"

            try:
                transform, width, height = calculate_default_transform(
                    src.crs, SET_CRS, src.width, src.height, *src.bounds
                )
                kwargs = src.meta.copy()
                kwargs.update({
                    "crs": SET_CRS,
                    "transform": transform,
                    "width": width,
                    "height": height
                })

                # Write re-projected dataset to a new file
                with rasterio.open(output_filepath, "w", **kwargs) as dst:
                    for i in range(1, src.count + 1):  # Loop over all bands
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=SET_CRS,
                            resampling=Resampling.nearest
                        )

                filepath = output_filepath

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Reprojection failed: {e}")

    
    # Determine which URL to return
    if SERVER_ENV == "local":
        # file_path = str(filepath.absolute()).replace("\\", "/")
        file_url = f"file://{filepath}"
    else:
        file_url = f"http://localhost:8000/{filepath}"


    return {
        "filename": file.filename, 
        "file_url": file_url,
        "bounds": bounds,    
    }
