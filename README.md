# waypoint-planner
An interactive Bokeh application for exploring georeferenced images and planning waypoints. This app enables users to upload GeoTIFF images, visualize data, and dynamically create and optimize waypoint traversal paths. 

Designed neither for efficiency nor scalability, this app is a prototype for quick field use.


## Features
- **Interactive Image Viewer:** Upload GeoTIFF images with support for RGBA and 3-band formats.
- **Dynamic Waypoint Creation:** Click to place waypoints on the map.
- **Shortest Path Optimization:** Automatically compute the optimal traversal path for all waypoints.
- **File Downloads:** Save waypoints as a `.wpl` file for further use (e.g., in QGroundControl).
- **Responsive UI:** Built with Bokeh for a seamless, interactive experience.
- **Dockerized Deployment:** Fully containerized for portability and ease of deployment.

## Getting Started

### Prerequisites
1. **Python 3.10+**: Ensure Python is installed on your system.
2. **Docker**: Required for running the containerized version of the app.
3. **Bokeh**: Installable via `pip` (if running locally).

### Local Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/javelina-works/waypoint-planner.git
   cd waypoint-planner
   ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the app:
    ```bash
    bokeh serve planner --show --websocket-max-message-size=250000000
    ```

4. Open the app in your browser at http://localhost:5006/planner.

---

## **Deployment with Docker**

### **Building the Image**
1. Build the Docker image:
    ```bash
    docker build -t waypoint-planner .
    ```

2. Run the container:
    ```bash
    docker run -p 5006:5006 waypoint-planner
    ```

    OR to emulate the production environment:

    ```bash
    docker run --cpus="2" --memory="512m" --memory-swap="512m" -p 5006:5006 waypoint-planner 
    ```

## Usage Instructions

1. **Upload GeoTIFF Image:** Use the file upload widget to upload a GeoTIFF image.
2. **Add Waypoints:** Click on the map to place waypoints.
3. **Plan Shortest Path:** Click the "Plan Shortest Traversal" button to compute the optimal path.
4. **Download Waypoints:** Use the "Save to File" button to export the waypoints as a `.waypoints` file. (Compatible with [Mission Planner](https://ardupilot.org/planner/))

## Automated Build and Deployment

This repository uses GitHub Actions for CI/CD:
- **Build and Push Docker Image:** On every push to the `release` branch, the Docker image is built and pushed to GHCR.
- **Deployment to Railway:** After the image is pushed, the app is automatically deployed to Railway.

## License

This project is licensed under the [AGPL 3.0 License](LICENSE).
