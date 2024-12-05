from bokeh.plotting import curdoc
from utils.logging_utils import setup_logger
import logging

SESSION_CONTEXT = curdoc().session_context
logger = setup_logger(name="waypoint_planner", log_level=logging.INFO)

# Full document layout setup in app_hooks.py
planner_row = getattr(SESSION_CONTEXT, 'planner_row')
curdoc().add_root(planner_row)

logger.debug(f"Main document (main.py): {curdoc()}")
logger.info("Session document built!")

