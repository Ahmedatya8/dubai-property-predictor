# ── Base image ────────────────────────────────────────────────────────────────
# We use the official Python 3.9 slim image — matches your Anaconda environment.
# 'slim' means no unnecessary system packages, keeps the image small.
FROM python:3.9-slim

# ── Working directory inside the container ────────────────────────────────────
# All subsequent commands run from here.
# Think of it as cd /app inside the container.
WORKDIR /app

# ── Copy requirements first (Docker layer caching) ────────────────────────────
# Docker builds in layers. By copying requirements.txt before the rest of the
# code, Docker caches the pip install step. If you only change your code
# (not requirements), Docker skips reinstalling packages — much faster rebuilds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project files ────────────────────────────────────────────────────────
# Copy source code, API, and the saved model artifact.
COPY src/     ./src/
COPY api/     ./api/
COPY models/  ./models/

# ── Expose port ───────────────────────────────────────────────────────────────
# Tell Docker this container listens on port 8000.
# This doesn't publish the port — that happens at docker run time.
EXPOSE 8000

# ── Start command ─────────────────────────────────────────────────────────────
# This runs when the container starts.
# --host 0.0.0.0 makes it accessible outside the container (not just localhost).
# --port 8000 matches the EXPOSE above.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]