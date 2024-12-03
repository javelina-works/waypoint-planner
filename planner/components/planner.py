from bokeh.layouts import column, row
from bokeh.models import (
    CrosshairTool, TableColumn, DataTable, CustomJS,
    ColumnDataSource, PointDrawTool, Button, Div,
    FileInput, 
)

from utils.geo_utils import process_geotiff, plan_traversal

def create_file_upload():
    # FileInput widget
    file_input = FileInput(accept=".tif,.tiff")

    # Callback for file upload
    def upload_callback(attr, old, new):
        """Handle file upload."""
        file_contents = file_input.value
        if file_contents:
            process_geotiff(file_contents)  # Remove header and decode

    # Goes with file_input object
    # Moved here for scoping bc using globals like a dumbass
    file_input.on_change("value", upload_callback)

    return file_input


async def add_image_tools(image_figure, marker_source):
    crosshair = CrosshairTool()
    image_figure.add_tools(crosshair)

    # Create draggable markers
    # ==================================================
    points = image_figure.scatter(x="x", y="y", size=10, color="red", source=marker_source) # Add circle markers to the plot
    image_figure.line(x="x", y="y", source=marker_source, line_width=2, color="green")  # Line connecting points
    image_figure.text(x="x", y="y", text="label", source=marker_source, text_font_size="10pt", text_baseline="middle", color="yellow")

    draw_tool = PointDrawTool(renderers=[points], empty_value="1")
    image_figure.add_tools(draw_tool)
    image_figure.toolbar.active_tap = draw_tool  # Set PointDrawTool as the active tool



def create_data_col(image_figure, marker_source):

    # Div to display the coordinates
    # ==============================
    coords_display = Div(text="Mouse Coordinates: (x: --, y: --)", width=400, height=30)

    # CustomJS callback for updating coordinates
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
    save_button = Button(label="Save to File", button_type="success")
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

    data_col = column(coords_display, save_button, plan_button, data_table)
    data_col.width = 400
    data_col.min_width = 400
    data_col.sizing_mode = "scale_height"

    # planner_row = row(image_container, data_col)
    # planner_row.sizing_mode = "stretch_both"
    return data_col


