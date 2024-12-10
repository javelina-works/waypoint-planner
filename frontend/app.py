import os
import streamlit as st
from streamlit.components.v1 import html
from flask import Flask, send_file, request
from io import BytesIO
from rio_tiler.io import Reader

# Upload directory
UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Flask app for handling tile requests
flask_app = Flask(__name__)

@flask_app.route("/tiles/<filename>/<int:z>/<int:x>/<int:y>.png")
def serve_tile(filename, z, x, y):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return "File not found", 404

    try:
        with Reader(file_path) as cog:
            tile_data, mask = cog.tile(x, y, z)
            image = cog.render(tile_data, mask, img_format="PNG")
            return send_file(BytesIO(image), mimetype="image/png")
    except Exception as e:
        return f"Error generating tile: {e}", 500

# Streamlit app
st.title("Interactive Map with Tile Server")

# File upload
uploaded_file = st.file_uploader("Upload a GeoTIFF file", type=["tif"])
if uploaded_file:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Uploaded file saved to {file_path}")

    # Embed the map with tiles from the uploaded file
    map_html = f"""
    <div id="map" style="width: 100%; height: 500px;"></div>
    <script>
        var map = L.map('map').setView([0, 0], 1);
        L.tileLayer('/tiles/{uploaded_file.name}/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 18,
        }}).addTo(map);
    </script>
    """
    html(map_html, height=500)

# Start the Flask server
st.server.mount_flask_app(flask_app, "/")
