# Base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /backend

# Install system dependencies required by Rasterio and other libraries
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libexpat1 \
    && apt-get clean

# Copy requirements file to the container
COPY requirements.txt /backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY app /backend/app
# Does not copy .db file to running container!
# COPY ../frontend/dist ./frontend/dist

# Expose the FastAPI default port
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
