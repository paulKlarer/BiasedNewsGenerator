
# Use an NVIDIA CUDA runtime base image with Ubuntu
FROM nvidia/cuda:12.8.1-devel-ubuntu22.04

ENV WANDB_API_KEY=4cf9d26370d9ec33ecd70d8a4d2e3cd3ce28019b
# Install Python 3.11 and other required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3.11 \
      python3.11-dev \
      python3.11-venv \
      python3.11-distutils \
      curl && \
    rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Install pipenv
RUN pip install pipenv

# # Set working directory
# WORKDIR /app

# Copy your application code
COPY . .

# Install your Python dependencies using pipenv
RUN pipenv install

# Expose the desired port
EXPOSE 8000

# Set the command to run your application
CMD ["pipenv", "run", "prod"]



