from bokeh.plotting import figure
from bokeh.models import Range1d



def create_image_figure(image_source):
    """Create the Bokeh figure for displaying the image."""

    bounds = image_source.data["bounds"][0]

    p = figure(
        title="Interactive GeoTIFF Viewer",
        x_range=Range1d(bounds.left, bounds.right),
        y_range=Range1d(bounds.bottom, bounds.top),
        match_aspect=True,
        active_scroll="wheel_zoom",
        tools="pan,wheel_zoom,reset",  # Enable panning and zooming
        sizing_mode="scale_height",  # Adjust figure height to viewport height
        # syncable=False, # Try to reduce network traffic
    )

    # Add the RGBA image to the plot
    p.image_rgba(
        image="image",
        source=image_source,
        x=bounds.left,
        y=bounds.bottom,
        dw=bounds.right - bounds.left,
        dh=bounds.top - bounds.bottom,
        # syncable=False, # Try to reduce network traffic
    )
    p.output_backend = "webgl" # In theory helps us with performance
    return p
