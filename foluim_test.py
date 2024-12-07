import folium
from rio_tiler.io import COGReader
from rio_tiler.profiles import img_profiles
from PIL import Image
import os

# Input GeoTIFF file path
geotiff_path = "input/ESPG-4326-orthophoto.tif"

# Output directory for tiles
output_dir = "tiles"
os.makedirs(output_dir, exist_ok=True)

# Open the GeoTIFF and generate a PNG overlay
with COGReader(geotiff_path) as cog:
    data, mask = cog.tile(0, 0, 0)  # Get a tile for zoom level 0
    img = Image.fromarray(data.transpose(1, 2, 0))  # Transpose to (Height, Width, Bands)
    img.save(os.path.join(output_dir, "overlay.png"))

# Path to the PNG overlay (generated above)
overlay_path = "tiles/overlay.png"





# Create a map centered at a specific location
m = folium.Map(location=[37.7749, -122.4194], zoom_start=10, tiles="OpenStreetMap")

# Add the overlay to the map
folium.raster_layers.ImageOverlay(
    image=overlay_path,
    bounds=[[37.7, -122.5], [37.8, -122.3]],  # Update with your GeoTIFF bounds
    opacity=0.7,
).add_to(m)


# Add a marker with a popup
folium.Marker(
    location=[37.7749, -122.4194],
    popup="San Francisco - Marker 1",
    tooltip="Click for more info",
    icon=folium.Icon(color="blue", icon="info-sign"),
).add_to(m)

# Add another marker with a different icon
folium.Marker(
    location=[37.8044, -122.2711],
    popup="Oakland - Marker 2",
    tooltip="Click for more info",
    icon=folium.Icon(color="green", icon="leaf"),
).add_to(m)

# Add a circle marker
folium.CircleMarker(
    location=[37.7607, -122.435],
    radius=50,
    popup="A large circle in SF",
    color="red",
    fill=True,
    fill_color="red",
).add_to(m)


# Add a layer control to toggle between map types with proper attributions
# folium.TileLayer(
#     tiles="Esri WorldImagery",
#     name="Terrain",
#     attr="Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors",
# ).add_to(m)

# folium.TileLayer(
#     tiles="BasemapAT orthofoto",
#     name="Toner",
#     attr="Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors",
# ).add_to(m)

# folium.TileLayer(
#     tiles="CartoDB positron",
#     name="CartoDB Positron",
#     attr="© OpenStreetMap contributors, © CartoDB",
# ).add_to(m)


# Add LayerControl
folium.LayerControl().add_to(m)

# Save the map to an HTML file
m.save("interactive_map.html")
