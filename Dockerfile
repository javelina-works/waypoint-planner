# Stage 1: Build the frontend
FROM node:16 AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Prepare backend
FROM python:3.10 AS backend
# Install system dependencies required by Rasterio and other libraries
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libexpat1 \
    && apt-get clean
WORKDIR /app/backend
COPY --from=frontend-builder /app/frontend/dist/ /app/frontend/dist
# COPY --from=frontend-builder /app/frontend/dist/ /app/frontend/dist
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./

EXPOSE 8000
# Run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# ENTRYPOINT ["tail", "-f", "/dev/null"]

# # Stage 3: Final image with Nginx
# FROM nginx:1.23
# WORKDIR /usr/share/nginx/html
# COPY --from=frontend-builder /app/frontend/dist/ ./
# COPY --from=backend /app/backend /app/backend
# COPY nginx.conf /etc/nginx/nginx.conf

# # Install supervisord
# RUN apt-get update && apt-get install -y supervisor
# COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# EXPOSE 80
# CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
