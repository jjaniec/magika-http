#!/usr/bin/env python3
"""
magika-http — FastAPI HTTP wrapper for Google Magika file-type detection.
"""

import time

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile
from magika import Magika
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from pydantic import BaseModel

from config import (
    API_SETTINGS,
    HOST,
    OTEL_EXPORTER_OTLP_ENDPOINT,
    OTEL_SDK_DISABLED,
    OTEL_SERVICE_NAME,
    PORT,
)
from swagger import setup_swagger_docs

# ---------------------------------------------------------------------------
# OpenTelemetry setup
# ---------------------------------------------------------------------------

_resource = Resource.create({"service.name": OTEL_SERVICE_NAME})
_provider = TracerProvider(resource=_resource)

if not OTEL_SDK_DISABLED:
    if OTEL_EXPORTER_OTLP_ENDPOINT:
        # Use OTLP gRPC exporter when an endpoint is configured
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        _otlp_exporter = OTLPSpanExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT)
        _provider.add_span_processor(BatchSpanProcessor(_otlp_exporter))
    else:
        # Fall back to console exporter so spans are visible during local dev
        _provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

trace.set_tracer_provider(_provider)
tracer = trace.get_tracer(__name__)

# ---------------------------------------------------------------------------
# Magika singleton — model is loaded once at import time
# ---------------------------------------------------------------------------

_magika = Magika()

# Warm the model with a tiny probe so /healthz reflects actual readiness
_warm_result = _magika.identify_bytes(b"")
_model_ready: bool = _warm_result is not None

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ContentTypeInfo(BaseModel):
    label: str
    mime_type: str
    group: str
    description: str
    extensions: list[str]
    is_text: bool


class ScanResult(BaseModel):
    ok: bool
    label: str
    mime_type: str
    group: str
    description: str
    extensions: list[str]
    is_text: bool
    score: float
    scan_duration_ms: float


class HealthResponse(BaseModel):
    status: str
    model_ready: bool
    model_version: str
    magika_version: str


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title=API_SETTINGS["title"],
    description=API_SETTINGS["description"],
    version=API_SETTINGS["version"],
    docs_url="/docs",
    redoc_url="/redoc",
)

FastAPIInstrumentor().instrument_app(app)
setup_swagger_docs(app)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/healthz", response_model=HealthResponse, tags=["Health"])
def healthz() -> HealthResponse:
    """
    Health check endpoint.

    Returns service status and confirms the Magika model is loaded and ready
    to process requests.
    """
    if not _model_ready:
        raise HTTPException(status_code=503, detail="Magika model not ready")

    return HealthResponse(
        status="ok",
        model_ready=_model_ready,
        model_version=_magika.get_model_name(),
        magika_version=_magika.get_module_version(),
    )


@app.post("/scan", response_model=ScanResult, tags=["Scan"])
async def scan(file: UploadFile) -> ScanResult:
    """
    Identify the content type of an uploaded file using Google Magika.

    Accepts any file via multipart/form-data and returns the detected content
    type together with confidence score and scan duration.
    """
    content = await file.read()

    with tracer.start_as_current_span("magika.scan") as span:
        span.set_attribute("file.name", file.filename or "unknown")
        span.set_attribute("file.size_bytes", len(content))

        t0 = time.perf_counter()
        result = _magika.identify_bytes(content)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        span.set_attribute("magika.scan_duration_ms", elapsed_ms)
        span.set_attribute("magika.result.ok", result.ok)

        if result.ok:
            span.set_attribute("magika.result.label", result.output.label)
            span.set_attribute("magika.result.mime_type", result.output.mime_type)
            span.set_attribute("magika.result.score", result.score)

    if not result.ok:
        raise HTTPException(
            status_code=422,
            detail=f"Magika could not identify file: {result.status}",
        )

    return ScanResult(
        ok=result.ok,
        label=result.output.label,
        mime_type=result.output.mime_type,
        group=result.output.group,
        description=result.output.description,
        extensions=result.output.extensions,
        is_text=result.output.is_text,
        score=result.score,
        scan_duration_ms=round(elapsed_ms, 3),
    )


# ---------------------------------------------------------------------------
# Dev entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
