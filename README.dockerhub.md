# magika-http

> HTTP wrapper for [Google Magika](https://github.com/google/magika) — AI-powered file-type detection.

Send any file to this service over HTTP and get back accurate content-type information powered by Magika's deep-learning model (~99% accuracy across 200+ content types).

**Source:** [github.com/jjaniec/magika-http](https://github.com/jjaniec/magika-http)

---

## Tags

| Tag | Description |
|-----|-------------|
| `latest` | Most recent build |
| `<magika-version>` (e.g. `1.0.2`) | Build pinned to that Magika release |

Images are rebuilt automatically **every Sunday at midnight UTC** to pick up OS and dependency updates.

---

## Quick start

```bash
docker run -p 8080:8080 jjaniec/magika-http
```

### Scan a file

```bash
curl -X POST http://localhost:8080/scan \
  -F "file=@/path/to/your/file"
```

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

### Health check

```bash
curl http://localhost:8080/healthz
```

```json
{
  "status": "ok",
  "model_ready": true,
  "model_version": "standard_v3_3",
  "magika_version": "1.0.2"
}
```

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/healthz` | Health check — confirms the model is loaded and ready |
| `POST` | `/scan` | Identify the content type of an uploaded file |
| `GET` | `/docs` | Interactive Swagger UI |
| `GET` | `/redoc` | ReDoc API documentation |

---

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Port the server listens on |
| `HOST` | `0.0.0.0` | Host the server binds to |
| `OTEL_SERVICE_NAME` | `magika-http` | OpenTelemetry service name |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _(empty)_ | OTLP gRPC collector endpoint. When unset, spans are printed to stdout |

### With OpenTelemetry export

```bash
docker run -p 8080:8080 \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317 \
  -e OTEL_SERVICE_NAME=magika-http \
  jjaniec/magika-http
```

---

## OpenTelemetry instrumentation

- **Auto-instrumentation** — every HTTP request produces a span (method, route, status code, latency)
- **`magika.scan` span** — emitted on every `/scan` call with attributes:
  - `file.name`, `file.size_bytes`
  - `magika.scan_duration_ms` — inference time in milliseconds
  - `magika.result.label`, `magika.result.mime_type`, `magika.result.score`
