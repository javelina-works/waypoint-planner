from bokeh.layouts import column, row
from bokeh.models import (
    CrosshairTool, TableColumn, DataTable, CustomJS,
    PointDrawTool, Button, Div, FileInput, Range1d, 
)
from bokeh.plotting import curdoc
from functools import partial

from utils.geo_utils import process_geotiff, plan_traversal

IMAGE_DOWNSAMPLE = 5 # Ratio by which size reduced 


def create_file_upload(image_source, image_figure, logger):
    # FileInput widget
    file_upload = FileInput(accept=".tif,.tiff")

    async def process_and_update(file_contents):
        rgba_image, bounds = process_geotiff(file_contents, logger, downsample_factor=IMAGE_DOWNSAMPLE)
        image_source.data = {"image": [rgba_image], "bounds": [bounds]}
        logger.debug(f"Updated figure bounds to: x_range=({bounds.left}, {bounds.right}), y_range=({bounds.bottom}, {bounds.top})")

        bounds = image_source.data["bounds"][0]
        # image_figure = getattr(SERVER_CONTEXT, 'image_figure')

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
            curdoc().add_next_tick_callback(partial(process_and_update, file_contents=file_contents))
            logger.debug("Image processing completed")

        except Exception as e:
            logger.error(f"Error during file upload: {e}", exc_info=True)

    # Goes with file_input object
    file_upload.on_change("value", upload_callback)

    return file_upload


def add_image_tools(image_figure, marker_source):
    crosshair = CrosshairTool(line_alpha=0.7, line_color="aquamarine")
    image_figure.add_tools(crosshair)

    # Create draggable markers
    # ==================================================
    points = image_figure.scatter(x="x", y="y", size=10, color="red", source=marker_source) # Add circle markers to the plot
    image_figure.line(x="x", y="y", source=marker_source, line_width=2, color="green")  # Line connecting points
    image_figure.text(x="x", y="y", text="label", source=marker_source, text_font_size="10pt", text_baseline="middle", color="yellow")

    draw_tool = PointDrawTool(renderers=[points], empty_value="1")
    image_figure.add_tools(draw_tool)
    image_figure.toolbar.active_tap = draw_tool  # Set PointDrawTool as the active tool


# @without_document_lock
def create_data_col(image_figure, marker_source):

    # Div to display mouse coordinates
    # ==============================
    coords_display = Div(text="Mouse Coordinates: (x: --, y: --)", width=400, height=30)
    callback = CustomJS(args=dict(coords=coords_display), code="""
        const {x, y} = cb_obj; // Get the mouse event from cb_obj
        // Update the Div text with the new coordinates
        coords.text = `Mouse Coordinates: (x: ${x.toFixed(7)}, y: ${y.toFixed(7)})`;
    """)

    # Attach the CustomJS to the plot's mouse move event
    image_figure.js_on_event("mousemove", callback)
    

    # Button to save mission data to file
    # =====================================
    js_save_file = """
    const data = source.data;
    let fileContent = "QGC WPL 110\\n";  // Header for the MAVLink file
    const numPoints = data['x'].length; // Number of rows

    if (numPoints === 0) {
        alert("No points to save!");
        return;
    }

    // Add home point (index 0)
    fileContent += `0\\t1\\t0\\t3\\t0\\t0\\t0\\t0\\t${data['y'][0]}\\t${data['x'][0]}\\t100.000000\\t1\\n`;

    // Add waypoints starting from index 1
    for (let i = 1; i < numPoints; i++) {
        fileContent += `${i}\\t0\\t0\\t16\\t0\\t0\\t0\\t0\\t${data['y'][i]}\\t${data['x'][i]}\\t100.000000\\t1\\n`;
    }

    // Create a downloadable blob
    const blob = new Blob([fileContent], { type: "text/plain" });
    const url = URL.createObjectURL(blob);

    // Create a temporary anchor element for download
    const a = document.createElement("a");
    a.href = url;
    a.download = "planned.waypoints";
    a.style.display = "none";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a); // Cleanup
    URL.revokeObjectURL(url);
    """

    # Create a Bokeh Button
    save_button = Button(label="Save Plan to File", button_type="success")
    file_download = CustomJS(args=dict(source=marker_source), code=js_save_file)
    save_button.js_on_click(file_download) # Attach the JS callback to the button


    # Traveling salesman solver
    # ======================================
    def update_marker_source_with_path(marker_source):
        """
        Update marker_source with the traversal path.

        Parameters:
            marker_source: ColumnDataSource
                The source containing x, y, and label of points.
        """
        # Get the optimal path
        traversal_order = plan_traversal(marker_source)

        # Reorder data based on traversal path
        data = marker_source.data
        new_data = {
            "x": [data["x"][i] for i in traversal_order],
            "y": [data["y"][i] for i in traversal_order],
            "label": [data["label"][i] for i in traversal_order],
        }

        # Update the ColumnDataSource
        marker_source.data = new_data

    # Attach callback to button
    def on_plan_click():
        update_marker_source_with_path(marker_source)

    plan_button = Button(label="Plan Shortest Traversal", button_type="primary")
    plan_button.on_click(on_plan_click)

    # Callback to clear all waypoints
    def clear_all_waypoints():
        marker_source.data = {"x": [], "y": [], "label": []}

    # Callback to delete the last waypoint
    def delete_last_waypoint():
        if len(marker_source.data["x"]) > 0:
            marker_source.data = {
                "x": marker_source.data["x"][:-1],
                "y": marker_source.data["y"][:-1],
                "label": marker_source.data["label"][:-1],
            }


    # Create the buttons
    clear_button = Button(label="Clear All Waypoints", button_type="danger")
    delete_button = Button(label="Delete Last Waypoint", button_type="warning")

    # Link the buttons to their callbacks
    clear_button.on_click(clear_all_waypoints)
    delete_button.on_click(delete_last_waypoint)


    # DataTable to display clicked waypoints
    # ======================================
    columns = [
        TableColumn(field="label", title="Waypoint #"),
        TableColumn(field="x", title="X Coordinate"),
        TableColumn(field="y", title="Y Coordinate"),
    ]
    data_table = DataTable(source=marker_source, columns=columns, width=400, height=280)

    # CustomJS to number points incrementally
    # Good: Faster to handle this in the browser
    js_callback = CustomJS(args=dict(source=marker_source), code="""
        const data = source.data;
        const labels = data['label'];
        for (let i = 0; i < data['x'].length; i++) {
            labels[i] = (i + 1).toString();  // Incremental numbering starts from 1
        }
        source.change.emit();  // Trigger update
    """)
    marker_source.js_on_change('data', js_callback)


    # Organize interactive image into a column layout
    # ===============================================
    # image_container = column(image_figure)
    # image_container.sizing_mode = "stretch_both"

    route_buttons = row(plan_button, save_button)
    point_buttons = row(delete_button, clear_button)

    data_col = column(coords_display, route_buttons, point_buttons, data_table)
    data_col.width = 400
    data_col.min_width = 400
    data_col.sizing_mode = "scale_height"

    # planner_row = row(image_container, data_col)
    # planner_row.sizing_mode = "stretch_both"
    return data_col


