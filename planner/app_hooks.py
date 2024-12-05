from bokeh.models import ColumnDataSource
from bokeh.layouts import column, row
from bokeh.io import curdoc
from utils.logging_utils import setup_logger
import logging
from utils.geo_utils import process_geotiff
from components.map import create_image_figure
from components.planner import create_file_upload, create_data_col

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
    # setattr(server_context, 'image_figure', image_figure)

    logger.debug(f"Server document (on_server_loaded): {curdoc()}")
    logger.info("Data initialized.")


# If present, this function executes when the server creates a session.
def on_session_created(session_context):
    """Create a session-specific layout."""

    # assert curdoc() == session_context.document, "Mismatch between curdoc() and session_context.document!"


    logger = setup_logger(name="waypoint_planner", log_level=logging.DEBUG)

    logger.debug(f"Session document (on_session_created): {curdoc()}")
    logger.debug(f"Session context: {session_context.id}")
    # logger.debug(f"Session context: {curdoc().session_context.id}")
    logger.debug(f"on_session_created curdoc(): {id(curdoc())}")
    logger.debug(f"Current document: {curdoc()}")
    logger.debug(f"Document roots before adding layout: {curdoc().roots}")

    # server_context = session_context.server_context
    initialize_data(session_context, logger)

    image_source = getattr(session_context, 'image_source')
    marker_source = getattr(session_context, 'marker_source')

    logger.debug(f'image_source: {image_source}')

    # Create a fresh image figure for this session
    image_figure = create_image_figure(image_source)

    # Create the session-specific layout
    # file_upload = FileInput(title="Select files:", accept=".tif,.tiff")
    file_upload = create_file_upload()

    # Define layout and add to the document
    image_container = column(file_upload, image_figure)
    image_container.sizing_mode = "stretch_both"

    data_col = create_data_col(image_figure, marker_source)
    planner_row = row(image_container, data_col)
    planner_row.sizing_mode = "stretch_both"

    logger.debug(f"planner_row: {planner_row}")
    logger.debug(f"image_container: {image_container}")
    logger.debug(f"data_col: {data_col}")


    # session_context.document.add_root(planner_row)
    # curdoc().add_root(planner_row)
    setattr(session_context, 'planner_row', planner_row)

    logger.debug(f"Document roots after adding layout: {curdoc().roots}")