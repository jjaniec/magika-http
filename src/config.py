"""
Configuration module for magika-http.
"""

import os

# API settings
API_SETTINGS = {
    "title": "magika-http",
    "description": "HTTP microservice wrapper for Google Magika AI-powered file-type detection",
    "version": "1.0.0",
}

# OpenTelemetry settings
OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "magika-http")
OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")

# Server settings
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")
