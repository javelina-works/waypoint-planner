import numpy as np
from rasterio.io import MemoryFile
from rasterio.plot import reshape_as_image
from matplotlib import cm
import os
import base64


def process_geotiff(file_contents, logger):
    """Load and preprocess GeoTIFF."""
    # global r_norm, g_norm, b_norm, non_transparent_mask, rgba_image, alpha, bounds

    decoded = None  # To hold the decoded or raw data
    # file_contents = fix_base64_padding(file_contents) # Fix padding before decoding

    # Handle local file or uploaded file
    if os.path.isfile(file_contents):
        logger.debug("Loaded GeoTIFF from local file.")
        with open(file_contents, "rb") as f:
            decoded = f.read()

    elif "," in file_contents:
        logger.debug("Uploaded file with Base64 header.")
        _, encoded = file_contents.split(",", 1)
        decoded = base64.b64decode(encoded)

    else:
        logger.debug("Uploaded file without Base64 header.")
        decoded = base64.b64decode(file_contents)

    try:
        with MemoryFile(decoded) as memfile:
            with memfile.open() as src:
                logger.debug(f"Band Data Type: {src.dtypes[0]}")  # e.g., 'uint8', 'uint16', 'float32'
                logger.debug(f"Value Range: Min={src.read(1).min()}, Max={src.read(1).max()}")
                logger.debug(f"The image has {src.count} bands.")
                image, bounds = extract_image_data(src)
    except Exception as e:
        logger.error(f"Error during file processing: {e}", exc_info=True)

    logger.debug("Success processing image")
    return image, bounds

def inspect_index(index):
    print("Index count:", np.size(index))
    print("Index min:", np.nanmin(index))
    print("Index max:", np.nanmax(index))
    print("Index mean:", np.nanmean(index))
    print("Index median:", np.nanmedian(index))
    print("Index std:", np.nanstd(index))

def extract_image_data(src):
    """
    Extract RGBA image and bounds from GeoTIFF.
    """

    if src.dtypes[0] == 'uint8':
        # Read all 4 bands at once (shape: 4 x height x width)
        bands = src.read([1, 2, 3, 4]).astype(np.float32)  # R, G, B, A

        # Normalize bands (axis=1,2 applies normalization per band)
        mins = bands.min(axis=(1, 2), keepdims=True)
        ptps = np.ptp(bands, axis=(1, 2), keepdims=True)
        norm_bands = (bands - mins) / np.where(ptps > 0, ptps, 1)  # Avoid division by zero

        # Transpose to height x width x 4 for RGBA format
        image = rgba_image = np.ascontiguousarray(np.transpose(norm_bands, (1, 2, 0)))

        # rgba_image = np.dstack(norm_bands)
        # norm_bands is (4, height, width)
        # rgba_image = (
        #     (norm_bands[0].astype(np.uint32) << 24) |  # Red channel
        #     (norm_bands[1].astype(np.uint32) << 16) |  # Green channel
        #     (norm_bands[2].astype(np.uint32) << 8)  |  # Blue channel
        #     (norm_bands[3].astype(np.uint32))          # Alpha channel
        # )

        rgba_image = np.flipud((image * 255).astype(np.uint8).view(dtype=np.uint32).reshape(image.shape[:2])) 

        # print(f"Same image? {np.array_equiv(tran_image,image)}")

        print(f"Bands shape: {bands.shape}")           # (4, height, width)
        print(f"Norm bands shape: {norm_bands.shape}")  # (height, width, 4)
        print(f"RGBA image shape: {rgba_image.shape}")  # (height, width)
        print(f"RGBA image min: {rgba_image.min()}, max: {rgba_image.max()}")
        print(f"RGBA image dtype: {rgba_image.dtype}")


        return rgba_image, src.bounds

    else:
        # r, g, b = [src.read(i).astype(float) for i in range(1, 4)]
        bands = src.read([1, 2, 3, 4])  # Shape: (3, height, width)
        r, g, b, a = bands
        
        print(f"Alpha datatype: {src.dtypes[3]}")
        r_norm = (r - np.min(r)) / (np.max(r) - np.min(r))
        g_norm = (g - np.min(g)) / (np.max(g) - np.min(g))
        b_norm = (b - np.min(b)) / (np.max(b) - np.min(b))
        alpha = (a - np.min(a)) / (np.max(a) - np.min(a))

        image = np.dstack((r_norm, g_norm, b_norm, alpha))
        rgba_image = np.flipud((image * 255).astype(np.uint8).view(dtype=np.uint32).reshape(image.shape[:2])) 

        bounds = src.bounds # Geographic bounds in WGS84

        return rgba_image, bounds


# def to_bokeh_rgba(image):
#     """Convert a normalized RGBA image to uint32 for Bokeh."""
#     return np.flipud((image * 255).astype(np.uint8).view(dtype=np.uint32).reshape(image.shape[:2]))


def calculate_index(index_name, bands, alpha, colormap="RdYlGn"):
    """Calculate vegetation index and return a normalized RGBA image."""
    r_norm, g_norm, b_norm = bands
    if index_name == "VARI":
        index = (g_norm - r_norm) / (g_norm + r_norm - b_norm + 1e-6)
    elif index_name == "GNDVI":
        index = (g_norm - b_norm) / (g_norm + b_norm + 1e-6)
    else:
        return None
    index = np.clip(index, -1, 1)
    index_norm = (index + 1) / 2
    colored_index = cm.get_cmap(colormap)(index_norm)
    colored_index[..., -1] = alpha
    return colored_index


def compute_histogram(index_data):
    """Compute histogram of vegetation index."""
    hist, edges = np.histogram(index_data, bins=125, range=(-1, 1))
    return hist, edges
