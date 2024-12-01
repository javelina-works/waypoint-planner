from bokeh.plotting import figure
from rasterio.io import MemoryFile
from matplotlib import cm
import numpy as np



def create_image_figure(bounds, image_source):
    """Create the Bokeh figure for displaying the image."""
    p = figure(
        title="Interactive GeoTIFF Viewer",
        x_range=(bounds.left, bounds.right),
        y_range=(bounds.bottom, bounds.top),
        active_scroll="wheel_zoom",
        tools="pan,wheel_zoom,reset",  # Enable panning and zooming
        sizing_mode="scale_height",  # Adjust figure height to viewport height
    )

    # Add the RGBA image to the plot
    p.image_rgba(
        image="image",
        source=image_source,
        x=bounds.left,
        y=bounds.bottom,
        dw=bounds.right - bounds.left,
        dh=bounds.top - bounds.bottom,
    )
    # p.output_backend = "webgl"
    return p


def process_geotiff(file_path):
    """Load and preprocess GeoTIFF."""
    with open(file_path, "rb") as f:
        decoded = f.read()
    with MemoryFile(decoded) as memfile:
        with memfile.open() as src:
            r, g, b = [src.read(i).astype(float) for i in range(1, 4)]
            r_norm, g_norm, b_norm = [
                (band - np.min(band)) / (np.max(band) - np.min(band))
                for band in (r, g, b)
            ]
            alpha = np.where((r == 0) & (g == 0) & (b == 0), 0, 1)
            rgba_image = np.dstack((r_norm, g_norm, b_norm, alpha))
            bounds = src.bounds
            return rgba_image, (r_norm, g_norm, b_norm), bounds

def update_image_from_upload(attr, old, new, file_input, image_source):
    """
    Handle image updates from uploaded files.
    """
    file_contents = file_input.value
    if not file_contents:
        return

    # Process the uploaded file
    rgba_image, bounds = process_geotiff(file_contents)

    # Update the ColumnDataSource
    image_source.data = {
        "image": [np.flipud((rgba_image * 255).astype(np.uint8).view(dtype=np.uint32).reshape(rgba_image.shape[:2]))],
    }
    return bounds


def to_bokeh_rgba(image):
    """
    Convert an RGBA array to uint32 for Bokeh.
    """
    return np.flipud((image * 255).astype(np.uint8).view(dtype=np.uint32).reshape(image.shape[:2]))


# def update_image(attr, old, new):
#     """Update the displayed image based on the selected view."""
#     new_image, new_index = calculate_index(view_select.value, color_select.value, spectrum_range.x_range.start)
#     image_source.data = {"image": [to_bokeh_rgba(new_image)]}

#     # Update histogram
#     hist, edges = compute_histogram(new_index)
#     midpoints = (edges[:-1] + edges[1:]) / 2
#     line_hist_source.data = {"x": midpoints, "y": hist}  # Update line graph source


