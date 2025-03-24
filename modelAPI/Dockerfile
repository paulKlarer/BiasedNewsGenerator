# FROM python:3.11-slim


# RUN apt-get update && apt-get install -y --no-install-recommends

# RUN pip install --upgrade pip && pip install pipenv

# COPY . .

# RUN pipenv install 

# EXPOSE 8000

# CMD ["pipenv", "run", "prod"]
# Use an NVIDIA CUDA runtime base image with Ubuntu
FROM nvidia/cuda:12.0.0-cudnn8-runtime-ubuntu22.04

# Install Python 3.11 and other required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3.11 \
      python3.11-venv \
      python3.11-distutils \
      curl && \
    rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Install pipenv
RUN pip install pipenv

# Set working directory
WORKDIR /app

# Copy your application code
COPY . .

# Install your Python dependencies using pipenv
RUN pipenv install

# Expose the desired port
EXPOSE 8000

# Set the command to run your application
CMD ["pipenv", "run", "prod"]



