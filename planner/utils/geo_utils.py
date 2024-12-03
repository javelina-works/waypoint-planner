import numpy as np
from rasterio.io import MemoryFile
from matplotlib import cm
import os
import base64
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment

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
                image = extract_image_data(src)
                bounds = src.bounds # Geographic bounds in WGS84
    except Exception as e:
        logger.error(f"Error during file processing: {e}", exc_info=True)

    logger.debug("Success processing image")
    return image, bounds

def extract_image_data(src):
    """
    Extract RGBA image and bounds from GeoTIFF.
    """
    num_bands = src.count
    # bounds = src.bounds # Geographic bounds in WGS84

    # Expecting [0,255] RGBA image (4 bands)
    if src.dtypes[0] == 'uint8' and num_bands == 4:
        bands = src.read([1, 2, 3, 4]).astype(np.uint8)  # R, G, B, A (shape: 4 x height x width)
        image = np.ascontiguousarray(np.transpose(bands, (1, 2, 0))) # Put first dim to end
        rgba_image = np.flipud(image.view(dtype=np.uint32).reshape(image.shape[:2])) # Bokeh image format
  
        return rgba_image

    # [0,255], but only 3 bands this time
    elif src.dtypes[0] == 'uint8' and num_bands == 3:
        r,g,b = src.read([1, 2, 3]).astype(np.uint8)  # R, G, B

        alpha = np.where((r == 0) & (g == 0) & (b == 0), 0, 255).astype(np.uint8)  # Fully opaque except where RGB is all 0
        image = np.dstack((r, g, b, alpha)) # Add in our artifical alpha channel
        rgba_image = np.flipud(image.view(dtype=np.uint32).reshape(image.shape[:2])) # Bokeh image format
  
        return rgba_image

    else:
        r,g,b = src.read([1, 2, 3]).astype(np.float32)  # R, G, B
        
        r_norm = (r - np.min(r)) / (np.max(r) - np.min(r))
        g_norm = (g - np.min(g)) / (np.max(g) - np.min(g))
        b_norm = (b - np.min(b)) / (np.max(b) - np.min(b))

        if num_bands == 4:
            a = src.read(4).astype(np.float32) # Read the alpha channel if it exists
            alpha = (a - np.min(a)) / (np.max(a) - np.min(a))
        else:
            alpha = np.where((r == 0) & (g == 0) & (b == 0), 0, 1).astype(float) # Create alpha channel

        image = np.dstack((r_norm, g_norm, b_norm, alpha))
        rgba_image = np.flipud((image * 255).astype(np.uint8).view(dtype=np.uint32).reshape(image.shape[:2])) 

        return rgba_image


def plan_traversal(marker_source):
    """
    Plan the shortest traversal path for the given markers.
    Uses a heuristic for the Traveling Salesman Problem (TSP).

    Parameters:
        marker_source: ColumnDataSource
            The source containing x, y, and label of points.

    Returns:
        List of indices representing the traversal order.
    """
    data = marker_source.data
    x_coords = data["x"]
    y_coords = data["y"]

    # Ensure we have points to process
    if len(x_coords) < 2:
        return list(range(len(x_coords)))  # No need for traversal if < 2 points

    # Combine x and y into coordinates
    points = np.array(list(zip(x_coords, y_coords)))

    # Compute pairwise distances
    distance_matrix = cdist(points, points, metric="euclidean")

    # Use a heuristic method to solve TSP (nearest neighbor)
    num_points = len(points)
    unvisited = set(range(num_points))
    path = []
    current = 0  # Start at the first point
    path.append(current)
    unvisited.remove(current)

    while unvisited:
        # Find the nearest neighbor
        nearest = min(unvisited, key=lambda point: distance_matrix[current, point])
        path.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    return path

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
