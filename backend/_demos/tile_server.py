from fastapi import FastAPI, HTTPException, Query
from starlette.responses import Response
from rio_tiler.io import Reader
from rio_tiler.profiles import img_profiles
import numpy as np
from rasterio.enums import Resampling
from io import BytesIO
from PIL import Image


app = FastAPI()

# Path to your COG file
COG_PATH = "output_cog.tif"

@app.get("/tiles/{z}/{x}/{y}.png")
def read_tile(
    z: int, x: int, y: int,
    rescale: str = Query(None, description="e.g. '0,255' to rescale pixels"),
    size: int = Query(256, description="Tile size in pixels, default 256")
):
    # size corresponds to the tilesize parameter in cog.tile()
    try:
        with Reader(COG_PATH) as cog:
            tile, mask = cog.tile(x, y, z, tilesize=size)
    except Exception as e:
        print("Error fetching tile:", e)  # Print the error for debugging
        # Out of bounds or another issue, return a blank tile or a 404
        blank_img = Image.new('RGBA', (256, 256), (0,0,0,0))
        buffer = BytesIO()
        blank_img.save(buffer, format="PNG")
        buffer.seek(0)
        return Response(buffer.read(), media_type='image/png')

    # If rescale is provided, apply it
    if rescale:
        try:
            rmin, rmax = map(float, rescale.split(','))
            # Clip and scale the tile data
            # tile shape: (bands, height, width)
            for b in range(tile.shape[0]):
                band = tile[b]
                # Stretch from (rmin, rmax) to (0, 255)
                band = ((band - rmin) / (rmax - rmin) * 255.0).clip(0, 255).astype(np.uint8)
                tile[b] = band
        except Exception as e:
            print("Rescale parameter invalid:", e)
            # If rescale fails, you can either return original tiles or raise an error.
            # We'll just ignore rescale if invalid.
            pass

    # Convert single-band to RGB if needed
    if tile.shape[0] == 1:
        tile = np.repeat(tile, 3, axis=0)

    # Add alpha channel
    tile = np.concatenate([tile, mask[np.newaxis, ...]], axis=0)
    img_array = tile.transpose((1, 2, 0))
    img = Image.fromarray(img_array)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return Response(buffer.read(), media_type="image/png")