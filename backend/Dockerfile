# Base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /backend

# Copy requirements file to the container
COPY requirements.txt /backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY app /backend/app

# Expose the FastAPI default port
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
