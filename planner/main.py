from bokeh.plotting import curdoc
from bokeh.layouts import column, row
from bokeh.models import (
    FileInput, Range1d, CrosshairTool, PointDrawTool,
    Div, CustomJS,
)
from utils.logging_utils import setup_logger
import logging

IMAGE_DOWNSAMPLE = 5 # Ratio by which size reduced 


SERVER_CONTEXT = curdoc().session_context.server_context

SESSION_CONTEXT = curdoc().session_context

logger = setup_logger(name="waypoint_planner", log_level=logging.DEBUG)
image_source = getattr(SERVER_CONTEXT, 'image_source')
marker_source = getattr(SERVER_CONTEXT, 'marker_source')
# image_figure = getattr(SERVER_CONTEXT, 'image_figure')

logger.debug(f'main.py Session Context: {curdoc().session_context.id}')
logger.debug(f"main.py curdoc(): {id(curdoc())}")

planner_row = getattr(SESSION_CONTEXT, 'planner_row')
curdoc().add_root(planner_row)

# Placeholder for bounds as a SimpleNamespace
# default_bounds = SimpleNamespace(left=0, right=1000, bottom=0, top=1000)

# async def process_and_update(file_contents):
#     rgba_image, bounds = process_geotiff(file_contents, logger, downsample_factor=IMAGE_DOWNSAMPLE)
#     image_source.data = {"image": [rgba_image], "bounds": [bounds]}
#     logger.debug(f"Updated figure bounds to: x_range=({bounds.left}, {bounds.right}), y_range=({bounds.bottom}, {bounds.top})")

#     bounds = image_source.data["bounds"][0]
#     # image_figure = getattr(SERVER_CONTEXT, 'image_figure')

#     # Get rid of possible previous image
#     image_figure.renderers = [
#         r for r in image_figure.renderers if not isinstance(r, type(image_figure.image_rgba))
#     ]

#     # Add a new renderer with the updated image
#     image_figure.image_rgba(
#         image="image",
#         source=image_source,
#         x=bounds.left,
#         y=bounds.bottom,
#         dw=bounds.right - bounds.left,
#         dh=bounds.top - bounds.bottom,
#     )

#     image_figure.update(
#         x_range = Range1d(bounds.left, bounds.right),
#         y_range = Range1d(bounds.bottom, bounds.top)
#     )
#     # image_figure.x_range = Range1d(bounds.left, bounds.right) # Update the figure bounds
#     # image_figure.y_range = Range1d(bounds.bottom, bounds.top)
    
#     # Make sure points on top of map image
#     image_figure.renderers = image_figure.renderers[-1:] + image_figure.renderers[:-1]

#     logger.debug("Updated image figure")
#     logger.debug(f"x_range=({image_figure.x_range.start}, {image_figure.x_range.end}), y_range=({image_figure.y_range.start}, {image_figure.y_range.end})")


# # Callback for file upload
# def upload_callback(attr, old, new):
#     """
#     Handle image updates from uploaded files.
#     """
#     try:
#         file_contents = file_upload.value
#         if not file_contents:
#             logger.warning("No file contents uploaded!")
#             return
          
#         logger.debug(f"Uploaded file size: {len(file_contents) / (1024 * 1024):.2f} MB")            
#         curdoc().add_next_tick_callback(partial(process_and_update, file_contents=file_contents))
#         logger.debug("Image processing completed")

#     except Exception as e:
#         logger.error(f"Error during file upload: {e}", exc_info=True)


# Bokeh application layout
#==========================
# image_figure = create_image_figure(image_source)

# file_upload = FileInput(title="Select files:", accept=".tif,.tiff")
# # file_upload.on_change("value", upload_callback)

# image_container = column(file_upload, image_figure)
# image_container.sizing_mode = "stretch_both"

# data_col = create_data_col(image_figure, marker_source)


# # Layout the widgets and figures
# # ==============================
# planner_row = row(image_container, data_col)
# planner_row.sizing_mode = "stretch_both"
# curdoc().add_root(planner_row)

logger.debug(f"Main document (main.py): {curdoc()}")
logger.info("   > Document built!")

