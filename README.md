# magika-http

HTTP microservice wrapper for [Google Magika](https://github.com/google/magika) — an AI-powered file-type detection tool.

Send files to the service over HTTP and get back accurate content-type information (MIME type, label, description, confidence score) powered by Magika's deep-learning model.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/healthz` | Health check — confirms the model is loaded and ready |
| `POST` | `/scan` | Identify the content type of an uploaded file |
| `GET` | `/docs` | Interactive Swagger UI |
| `GET` | `/redoc` | ReDoc API documentation |

### `GET /healthz`

```json
{
  "status": "ok",
  "model_ready": true,
  "model_version": "standard_v3_3",
  "magika_version": "1.0.2"
}
```

Returns `503` if the model failed to initialise.

### `POST /scan`

Accepts a file via `multipart/form-data` (field name: `file`).

```json
{
  "ok": true,
  "label": "python",
  "mime_type": "text/x-python",
  "group": "code",
  "description": "Python source",
  "extensions": ["py", "pyi"],
  "is_text": true,
  "score": 0.997,
  "scan_duration_ms": 3.142
}
```

## Running locally

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)

### Install and run

```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
./entrypoint.sh
```

The API is available at <http://localhost:8080>.

### Example `curl` commands

Health check:

```bash
curl http://localhost:8080/healthz
```

Scan a file:

```bash
curl -X POST http://localhost:8080/scan \
  -F "file=@/path/to/your/file"
```

Scan from stdin:

```bash
cat script.py | curl -X POST http://localhost:8080/scan \
  -F "file=@-;filename=script.py"
```

## Running with Docker

```bash
# Build
docker build -t magika-http .

# Run
docker run -p 8080:8080 magika-http
```

With OpenTelemetry export to a collector:

```bash
docker run -p 8080:8080 \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317 \
  -e OTEL_SERVICE_NAME=magika-http \
  magika-http
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Port the server listens on |
| `HOST` | `0.0.0.0` | Host the server binds to |
| `OTEL_SERVICE_NAME` | `magika-http` | OpenTelemetry service name |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _(empty)_ | OTLP gRPC collector endpoint. When unset, spans are printed to stdout |
| `OTEL_SDK_DISABLED` | `false` | Set to `true` to disable all OpenTelemetry tracing (suppresses console output when no collector is configured) |

## OpenTelemetry instrumentation

The service ships with two levels of instrumentation:

- **Auto-instrumentation** — `FastAPIInstrumentor` automatically creates spans for every HTTP request (method, route, status code, latency).
- **Manual span** — the `/scan` endpoint creates a `magika.scan` child span with the following attributes:
  - `file.name` — uploaded filename
  - `file.size_bytes` — size in bytes
  - `magika.scan_duration_ms` — time spent inside Magika's inference (milliseconds)
  - `magika.result.ok` — whether identification succeeded
  - `magika.result.label` — detected content type label
  - `magika.result.mime_type` — detected MIME type
  - `magika.result.score` — model confidence score

## Running tests

```bash
# Install dev dependencies
uv pip install -r requirements-dev.txt

# Run the test suite
pytest
```

## Generating the OpenAPI spec

```bash
python generate_swagger.py
```

This produces `swagger.yaml` and `swagger.json` at the repository root.

## Code quality

```bash
# Lint
ruff check .

# Format
ruff format .

# Auto-fix
ruff check --fix .
```

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.

Magika itself is also [Apache 2.0](https://github.com/google/magika/blob/main/LICENSE) and developed by Google.
