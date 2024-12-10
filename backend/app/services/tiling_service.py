# app/services/tiling_service.py
from rio_tiler.io import Reader
from rio_tiler.errors import TileOutsideBounds
from fastapi import HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Tuple
from io import BytesIO
import numpy as np
from PIL import Image


COG_PATH = "../output_cog.tif"

def get_tile(
        image_path: str, 
        x: int, y: int, z: int,
        rescale: str = Query(None, description="e.g. '0,255' to rescale pixels"),
        size: int = 256
    ) -> StreamingResponse:
    """
    Generate a tile for the given image at the specified tile coordinates (x, y, z).
    """

    # print(f"Reading file: {image_path} for tile (z={z}, x={x}, y={y})", flush=True)
    try:
        with Reader(image_path) as cog:
            tile_image  = cog.tile(x, y, z, tilesize=size)
            image_blob = tile_image.render(img_format="PNG")
            buffer = BytesIO(image_blob)
            buffer.seek(0)
            return StreamingResponse(buffer, media_type="image/png")

    except TileOutsideBounds as oob:
        # Out of bounds, return a blank tile or a 404
        print("Out of bounds tile request!")
        blank_img = Image.new('RGBA', (256, 256), (0,0,0,0))
        buffer = BytesIO()
        blank_img.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type='image/png')
    
    except HTTPException as e:
        print("HTTP exception:", e)
        return None

    except Exception as e:
        print("Error fetching tile:", e)  # Print the error for debugging
        raise
        

    # If rescale is provided, apply it
    # if rescale:
    #     try:
    #         rmin, rmax = map(float, rescale.split(','))
    #         # Clip and scale the tile data
    #         # tile shape: (bands, height, width)
    #         for b in range(tile.shape[0]):
    #             band = tile[b]
    #             # Stretch from (rmin, rmax) to (0, 255)
    #             band = ((band - rmin) / (rmax - rmin) * 255.0).clip(0, 255).astype(np.uint8)
    #             tile[b] = band
    #     except Exception as e:
    #         print("Rescale parameter invalid:", e)
    #         # If rescale fails, you can either return original tiles or raise an error.
    #         # We'll just ignore rescale if invalid.
    #         pass

    # # Convert single-band to RGB if needed
    # if tile.shape[0] == 1:
    #     tile = np.repeat(tile, 3, axis=0)

    # # Add alpha channel
    # tile = np.concatenate([tile, mask[np.newaxis, ...]], axis=0)
    # img_array = tile.transpose((1, 2, 0))
    # img = Image.fromarray(img_array)

    # buffer = BytesIO()
    # img.save(buffer, format="PNG")
    # buffer.seek(0)
    # return Response(buffer.read(), media_type="image/png")

    # return StreamingResponse(buff, media_type="image/png")
