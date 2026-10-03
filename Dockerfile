# ---------- stage 1: build the virtualenv with runtime deps ----------
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# requirements first, so this layer is cached until the deps actually change
COPY requirements.txt .
RUN pip install -r requirements.txt


# ---------- stage 2: test image (used by CI: docker build --target test) ----------
FROM builder AS test

WORKDIR /app
# requirements-dev.txt does "-r requirements.txt", so both files are needed here
COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements-dev.txt

COPY setup.cfg app.py ./
COPY aceest ./aceest
COPY tests ./tests

# "python -m pytest" (not plain pytest) so /app is on sys.path and "import aceest" works
CMD ["python", "-m", "pytest", "--cov=aceest", "--cov-report=term-missing"]


# ---------- stage 3: final runtime image (default target) ----------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    ACEEST_DB=/data/aceest_fitness.db

# don't run as root inside the container
RUN useradd --create-home --uid 1000 appuser \
    && mkdir /data \
    && chown appuser:appuser /data

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY app.py ./
COPY aceest ./aceest

USER appuser
VOLUME /data
EXPOSE 5000

# python is already in the image, so no need to install curl just for this
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
