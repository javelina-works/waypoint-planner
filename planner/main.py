from bokeh.plotting import curdoc
from bokeh.layouts import column, row
from bokeh.models import FileInput, Range1d
from types import SimpleNamespace

from utils.geo_utils import process_geotiff
from utils.logging_utils import setup_logger
import logging
from components.planner import create_data_col
# import cProfile


IMAGE_DOWNSAMPLE = 3.0 # Ratio by which size reduced 

SERVER_CONTEXT = curdoc().session_context.server_context

logger = setup_logger(name="waypoint_planner", log_level=logging.DEBUG)
image_source = getattr(SERVER_CONTEXT, 'image_source')
marker_source = getattr(SERVER_CONTEXT, 'marker_source')
image_figure = getattr(SERVER_CONTEXT, 'image_figure')


# Placeholder for bounds as a SimpleNamespace
default_bounds = SimpleNamespace(left=0, right=1000, bottom=0, top=1000)


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
        # image_source.data = {"image": [rgba_image], "bounds": [bounds]}
        image_source.patch({
            "image": [(0, rgba_image)],  # Update the first (and only) image
            "bounds": [(0, bounds)]     # Update the bounds
        })

        logger.debug(f"Updated figure bounds to: x_range=({bounds.left}, {bounds.right}), y_range=({bounds.bottom}, {bounds.top})")

    except Exception as e:
        logger.error(f"Error during file upload: {e}", exc_info=True)

# Callback for file upload
def update_figure(attr, old, new):
    try:
        bounds = image_source.data["bounds"][0]
        image_figure = getattr(SERVER_CONTEXT, 'image_figure')

        # Get rid of possible previous image
        image_figure.renderers = [
            r for r in image_figure.renderers if not isinstance(r, type(image_figure.image_rgba))
        ]

        # Add a new renderer with the updated image
        image_figure.image_rgba(
            image="image",
            source=image_source,
            x=bounds.left,
            y=bounds.bottom,
            dw=bounds.right - bounds.left,
            dh=bounds.top - bounds.bottom,
        )

        image_figure.update(
            x_range = Range1d(bounds.left, bounds.right),
            y_range = Range1d(bounds.bottom, bounds.top)
        )
        # image_figure.x_range = Range1d(bounds.left, bounds.right) # Update the figure bounds
        # image_figure.y_range = Range1d(bounds.bottom, bounds.top)
        
        # Make sure points on top of map image
        image_figure.renderers = image_figure.renderers[-1:] + image_figure.renderers[:-1]

        logger.debug("Updated image figure")
        logger.debug(f"x_range=({image_figure.x_range.start}, {image_figure.x_range.end}), y_range=({image_figure.y_range.start}, {image_figure.y_range.end})")

    except Exception as e:
        logger.error(f"Error during file upload: {e}", exc_info=True)

# Bokeh application layout
#==========================
file_upload = FileInput(title="Select files:", accept=".tif,.tiff")
file_upload.on_change("value", upload_callback, update_figure)

image_container = column(file_upload, image_figure)
image_container.sizing_mode = "stretch_both"

data_col = create_data_col(image_figure, marker_source)

# Layout the widgets and figures
planner_row = row(image_container, data_col)
planner_row.sizing_mode = "stretch_both"

curdoc().add_root(planner_row)
logger.info("Application started.")
