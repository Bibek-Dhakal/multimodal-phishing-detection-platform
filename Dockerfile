# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables to prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies required for compiling some Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.min.versions.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.min.versions.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose ports for both FastAPI and Streamlit (Optional here, handled in docker-compose)
EXPOSE 8000 8501
