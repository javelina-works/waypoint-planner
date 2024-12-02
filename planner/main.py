from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, FileInput, Range1d
from types import SimpleNamespace

import logging
from utils.logging_utils import setup_logger
from utils.geo_utils import process_geotiff
from components.planner import create_data_col
from components.map import create_image_figure

import cProfile

global image_figure

# Initialize logger
logger = setup_logger(name="waypoint_planner", log_level=logging.DEBUG)

# Initialize Data Sources
image_source = ColumnDataSource(data={"image": []})
marker_source = ColumnDataSource(data={"x": [], "y": [], "label": []})

# Placeholder for bounds as a SimpleNamespace
default_bounds = SimpleNamespace(left=0, right=1000, bottom=0, top=1000)


# tiff_file = "input/MADRID_RGB.tif"
tiff_file = "input/ESPG-4326-orthophoto.tif"

# Process initial data
logger.info("Processing initial GeoTIFF file.")
rgba_image, bounds = process_geotiff(tiff_file, logger)
image_source.data = {"image": [rgba_image]}

# Create figures
image_figure = create_image_figure(bounds, image_source)


# Callback for file upload
def upload_callback(attr, old, new):
    """
    Handle image updates from uploaded files.
    """
    try:
        file_contents = file_upload.value
        if not file_contents:
            logger.warning("No file contents uploaded!")
            return
        
        logger.debug(f"Uploaded file size: {len(file_contents) / (1024 * 1024):.2f} MB")

        rgba_image, bounds = process_geotiff(file_contents, logger)  # Remove header and decode
        image_source.data = {"image": [rgba_image]}

        # image_figure = create_image_figure(bounds, image_source)
        # Add a new renderer with the updated image
        image_figure.image_rgba(
            image="image",
            source=image_source,
            x=bounds.left,
            y=bounds.bottom,
            dw=bounds.right - bounds.left,
            dh=bounds.top - bounds.bottom,
        )

        image_figure.x_range = Range1d(bounds.left, bounds.right) # Update the figure bounds
        image_figure.y_range = Range1d(bounds.bottom, bounds.top)

        logger.debug(f"Updated figure bounds to: x_range=({bounds.left}, {bounds.right}), y_range=({bounds.bottom}, {bounds.top})")
        logger.debug(f"x_range=({image_figure.x_range.start}, {image_figure.x_range.end}), y_range=({image_figure.y_range.start}, {image_figure.y_range.end})")

    except Exception as e:
        logger.error(f"Error during file upload: {e}", exc_info=True)


# Bokeh application layout
#==========================
file_upload = FileInput(title="Select files:", accept=".tif,.tiff")
file_upload.on_change("value", upload_callback)

image_container = column(file_upload, image_figure)
image_container.sizing_mode = "stretch_both"

data_col = create_data_col(image_figure, marker_source)

# Layout the widgets and figures
planner_row = row(image_container, data_col)
planner_row.sizing_mode = "stretch_both"

curdoc().add_root(planner_row)
logger.info("Application started.")
