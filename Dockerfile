# syntax=docker/dockerfile:1
# Base image mirrors Google's own Magika Dockerfile (python:3.11-slim + pip install magika)
ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim

LABEL maintainer="Joffrey JANIEC"
LABEL description="HTTP microservice wrapper for Google Magika AI-powered file-type detection"

# Install uv for fast dependency installation
RUN pip install --no-cache-dir uv

WORKDIR /app

# Install dependencies first (layer-cache friendly)
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Copy application source
COPY . .

RUN chmod +x ./entrypoint.sh

EXPOSE 8080

CMD ["./entrypoint.sh"]
