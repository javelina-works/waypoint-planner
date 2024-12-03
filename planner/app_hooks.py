from bokeh.models import ColumnDataSource
from utils.logging_utils import setup_logger
import logging
from utils.geo_utils import process_geotiff
from components.map import create_image_figure


tiff_file = "input/MADRID_RGB.tif"



def on_server_loaded(server_context):
    """Function to run once when the server starts."""

    logger = setup_logger(name="waypoint_planner", log_level=logging.DEBUG)
    logger.info("Bokeh server has started!")
    initialize_data(server_context, logger)
    logger.info("Server startup completed.")


def initialize_data(server_context, logger):
    """Server data initialization task."""

    logger.info("Initializing data...")
    image_source = ColumnDataSource(data={"image": []})
    marker_source = ColumnDataSource(data={"x": [], "y": [], "label": []})

    logger.debug("Processing initial GeoTIFF file.")
    rgba_image, bounds = process_geotiff(tiff_file, logger)
    image_source.data = {"image": [rgba_image], "bounds": [bounds]}
    image_figure = create_image_figure(image_source)

    setattr(server_context, 'image_source', image_source)
    setattr(server_context, 'marker_source', marker_source)
    setattr(server_context, 'image_figure', image_figure)

    logger.info("Data initialized.")

