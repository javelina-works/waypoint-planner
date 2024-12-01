from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.models import Div, Select, Slider, Button, ColumnDataSource

from utils.logging_utils import setup_logger
import logging
from utils.geo_utils import process_geotiff, calculate_index, to_bokeh_rgba, compute_histogram
# from widgets import create_histogram_figures, create_image_figure, create_controls
from widgets.planner import create_data_col
from widgets.map import create_image_figure


# Initialize logger
logger = setup_logger(name="geo_tiff_app", log_level=logging.DEBUG)

# Initialize Data Sources
image_source = ColumnDataSource(data={"image": []})

# Initialize Global Variables
tiff_file = "input/MADRID_RGB.tif"

# Process initial data
logger.info("Processing initial GeoTIFF file.")
rgba_image, index_data, bounds = process_geotiff(tiff_file)
image_source.data = {"image": [to_bokeh_rgba(rgba_image)]}

# Create figures
image_figure = create_image_figure(bounds, image_source)

image_container = column(image_figure)
image_container.sizing_mode = "stretch_both"

# data_col = create_data_col(image_figure)

# Layout the widgets and figures
planner_row = row(image_container)
planner_row.sizing_mode = "stretch_both"

curdoc().add_root(planner_row)
logger.info("Application started.")
