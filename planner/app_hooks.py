from bokeh.models import ColumnDataSource
from bokeh.layouts import column, row
from bokeh.io import curdoc
from utils.logging_utils import setup_logger
import logging
from utils.geo_utils import process_geotiff
from components.map import create_image_figure
from components.planner import create_file_upload, create_data_col, add_image_tools

tiff_file = "input/MADRID_RGB.tif"



def on_server_loaded(server_context):
    """Function to run once when the server starts."""

    logger = setup_logger(name="waypoint_planner", log_level=logging.DEBUG)
    logger.info("Bokeh server has started!")
    # initialize_data(server_context, logger) # Wrong, needs session context
    logger.info("Server startup completed.")


def initialize_data(server_context, logger):
    """Server data initialization task."""

    logger.info("Initializing data...")
    image_source = ColumnDataSource(data={"image": []})
    marker_source = ColumnDataSource(data={"x": [], "y": [], "label": []})

    logger.debug("Processing initial GeoTIFF file.")
    rgba_image, bounds = process_geotiff(tiff_file, logger)
    image_source.data = {"image": [rgba_image], "bounds": [bounds]}

    setattr(server_context, 'image_source', image_source)
    setattr(server_context, 'marker_source', marker_source)

    logger.debug(f"Server document (on_server_loaded): {curdoc()}")
    logger.info("Data initialized.")


# If present, this function executes when the server creates a session.
def on_session_created(session_context):
    """Create a session-specific layout."""

    logger = setup_logger(name="waypoint_planner", log_level=logging.DEBUG)
    logger.debug(f'on_session_created: {id(session_context)}')

    # server_context = session_context.server_context
    initialize_data(session_context, logger)
    image_source = getattr(session_context, 'image_source')
    marker_source = getattr(session_context, 'marker_source')

    # Create the session-specific layout
    image_figure = create_image_figure(image_source) # Create a fresh image figure for this session
    file_upload = create_file_upload(image_source, image_figure, logger)

    # Define layout and add to the document
    image_container = column(file_upload, image_figure)
    image_container.sizing_mode = "stretch_both"

    add_image_tools(image_figure, marker_source)
    data_col = create_data_col(image_figure, marker_source)
    planner_row = row(image_container, data_col)
    planner_row.sizing_mode = "stretch_both"

    setattr(session_context, 'planner_row', planner_row) # Pass to session, add to doc there

    logger.debug(f"on_session_created complete: {curdoc().roots}")