# Trusted CA certificates

This folder is mounted read-only into the Ollama container at `/certs`, and Ollama is
configured with `SSL_CERT_DIR=/certs`, so any PEM-encoded `.crt`/`.pem` file you place
here is added to the container's trusted root store.

**You only need this if you are behind a TLS-inspecting proxy** (corporate firewall or
antivirus that scans HTTPS) and the Ollama model download fails with:

```
tls: failed to verify certificate: x509: certificate signed by unknown authority
```

## Quick setup (Windows)

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File certs\export-windows-cas.ps1
```

This writes `windows-roots.crt` here — every root CA your machine trusts (including the
proxy's). Then run `docker compose up`.

## Manual alternative

Drop your corporate root CA (PEM format, `.crt` or `.pem`) into this folder by any means.
Multiple files are fine; a single file may contain multiple concatenated certificates.

> `.crt` / `.pem` files here are gitignored — they never get committed.
