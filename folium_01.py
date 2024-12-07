import folium
from folium.plugins import Draw
import rasterio
from pyproj import Transformer


# Path to your COG
cog_path = "output_cog.tif"

# Step 1: Extract bounding box from the GeoTIFF
with rasterio.open(cog_path) as src:
    # Bounds: left, bottom, right, top in the dataset's CRS
    left, bottom, right, top = src.bounds
    dataset_crs = src.crs

# If the dataset is not in EPSG:4326 (WGS84 lat/lon), reproject the bounds
if dataset_crs != "EPSG:4326":
    transformer = Transformer.from_crs(dataset_crs, "EPSG:4326", always_xy=True)
    # Transform bounds from dataset CRS to lat/lon
    # Note: transformer.transform expects (x, y) order
    west, south = transformer.transform(left, bottom)
    east, north = transformer.transform(right, top)
else:
    # Already in lat/lon
    west, south, east, north = left, bottom, right, top


# Center the map on some approximate center of your dataset
m = folium.Map(max_zoom=21)

# -----------------------------------
# 1. Add Tiled Layer from GeoTIFF source (Pyramidal tiles)
# -----------------------------------
# Assume you have a local tile service running at http://localhost:5000
# The tile server is responsible for reading your GeoTIFF and serving tiles
# in a format similar to: /tiles/{z}/{x}/{y}.png
m = folium.Map(location=[40, -100], zoom_start=4)
folium.TileLayer(
    tiles='http://localhost:8000/tiles/{z}/{x}/{y}.png',
    attr='My COG Tiles',
    name='GeoTIFF COG Layer',
    overlay=True,
    max_zoom=22,
).add_to(m)

# folium expects [[south, west], [north, east]] for fit_bounds
m.fit_bounds([[south, west], [north, east]])

# -----------------------------------
# 2. Progressive rendering:
# Handled by the tile server + tile layer above.
# As you zoom in and out, Folium/Leaflet will request appropriate tiles.
# -----------------------------------

# -----------------------------------
# 3. Clicking to add waypoints (markers):
# The ClickForMarker plugin adds a marker where the user clicks.
# Note: This plugin places a single marker. Subsequent clicks move that marker.
# If you prefer multiple markers, you could handle that differently or use Draw.
# -----------------------------------
folium.ClickForMarker(popup="Waypoint").add_to(m)

# Alternatively, you can rely entirely on the Draw plugin to add markers:
# The Draw plugin supports adding markers by selecting the "marker" tool.
# Just omit ClickForMarker if using Draw’s marker tool.

# -----------------------------------
# 4. Define a region of interest using a polygon:
# The Draw plugin allows drawing polygons. Set 'polygon' to True in draw options.
# Users can also draw rectangles, lines, and circles, depending on the options given.
# -----------------------------------
draw = Draw(
    draw_options={
        'polyline': True,
        'polygon': True,
        'rectangle': True,
        'circle': True,
        'marker': True,
        'circlemarker': False
    },
    edit_options={
        'edit': True,   # Allows editing the shapes
        'remove': True  # Allows deleting the shapes
    }
)
draw.add_to(m)

# -----------------------------------
# 5. Move/Delete waypoints:
# The Draw plugin’s edit options allow users to move shapes (including markers)
# and delete them if desired.
# When a marker is placed using the Draw plugin, you can switch to edit mode 
# to drag it to a new location or remove it entirely.
# -----------------------------------

# Add Layer Control to toggle layers on/off
folium.LayerControl().add_to(m)

# Save map to an HTML file
m.save('interactive_map_01.html')
print("Map saved as 'interactive_map_01.html'. Open it in a browser to interact.")
