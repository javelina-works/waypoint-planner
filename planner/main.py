from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource

from utils.logging_utils import setup_logger
import logging
from utils.geo_utils import process_geotiff, calculate_index, to_bokeh_rgba, compute_histogram
from components.planner import create_data_col
from components.map import create_image_figure


# Initialize logger
logger = setup_logger(name="geo_tiff_app", log_level=logging.DEBUG)

# Initialize Data Sources
image_source = ColumnDataSource(data={"image": []})

# Placeholder for bounds
default_bounds = {"left": 0, "right": 1000, "bottom": 0, "top": 1000}

# Initialize Global Variables
tiff_file = "input/MADRID_RGB.tif"

# Process initial data
logger.info("Processing initial GeoTIFF file.")
rgba_image, index_data, bounds = process_geotiff(tiff_file)
image_source.data = {"image": [to_bokeh_rgba(rgba_image)]}

# Create figures
image_figure = create_image_figure(default_bounds, image_source)

image_container = column(image_figure)
image_container.sizing_mode = "stretch_both"

data_col = create_data_col(image_figure)

# Layout the widgets and figures
planner_row = row(image_container, data_col)
planner_row.sizing_mode = "stretch_both"

curdoc().add_root(planner_row)
logger.info("Application started.")
