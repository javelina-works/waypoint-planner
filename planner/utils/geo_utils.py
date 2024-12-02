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
    # r, g, b = [src.read(i).astype(float) for i in range(1, 4)]
    bands = src.read([1, 2, 3, 4])  # Shape: (3, height, width)
    r, g, b, alpha = bands
    
    inspect_index(alpha)
    # inspect_index(g)
    # inspect_index(b)
    print(f"Alpha datatype: {src.dtypes[3]}")
    r_norm = (r - np.min(r)) / (np.max(r) - np.min(r))
    g_norm = (g - np.min(g)) / (np.max(g) - np.min(g))
    b_norm = (b - np.min(b)) / (np.max(b) - np.min(b))
    alpha = np.where((r == 0) & (g == 0) & (b == 0), 0, 1)

    inspect_index(r_norm)

    # Determine if normalization is necessary
    if src.dtypes[0] != 'uint8' or np.max(bands) > 255:
        print("Normalizing bands...")
        mins = np.min(bands, axis=(1, 2), keepdims=True)  # Only normalize RGB
        maxs = np.max(bands, axis=(1, 2), keepdims=True)
        bands = (bands - mins) / (maxs - mins) * 255  # Scale back to [0, 255]

    # r, g, b, alpha = bands
    # Use the existing alpha band directly
    # alpha = (alpha / np.max(alpha) * 255).astype(np.uint8)  # Ensure alpha is in [0, 255]
    # alpha = np.where(np.all(bands[:2] == 0, axis=0), 0, 1)
    alpha = np.where((r == 0) & (g == 0) & (b == 0), 0, 1)

    # Construct RGBA image
    # image = np.dstack((r, g, b, alpha))
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
