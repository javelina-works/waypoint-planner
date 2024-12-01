from bokeh.plotting import figure


def create_image_figure(bounds, image_source):
    """Create the Bokeh figure for displaying the image."""
    p = figure(
        title="Interactive GeoTIFF Viewer",
        x_range=(bounds.left, bounds.right),
        y_range=(bounds.bottom, bounds.top),
        active_scroll="wheel_zoom",
        tools="pan,wheel_zoom,reset",  # Enable panning and zooming
        sizing_mode="scale_height",  # Adjust figure height to viewport height
    )

    # Add the RGBA image to the plot
    p.image_rgba(
        image="image",
        source=image_source,
        x=bounds.left,
        y=bounds.bottom,
        dw=bounds.right - bounds.left,
        dh=bounds.top - bounds.bottom,
    )
    # p.output_backend = "webgl"
    return p


