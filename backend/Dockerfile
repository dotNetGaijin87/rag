FROM python:3.12-slim

# Set INSECURE_TLS=1 at build time if you are behind a TLS-inspecting proxy
# (corporate firewall / antivirus SSL scanning) whose root CA the container
# does not trust. It relaxes certificate checks for the package index only.
ARG INSECURE_TLS=0

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN if [ "$INSECURE_TLS" = "1" ]; then \
        pip install --no-cache-dir \
            --trusted-host pypi.org \
            --trusted-host files.pythonhosted.org \
            -r requirements.txt; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

COPY . .

EXPOSE 8000

# 2 workers, long timeout because local LLM/embedding calls can be slow on CPU.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "600", "wsgi:app"]
