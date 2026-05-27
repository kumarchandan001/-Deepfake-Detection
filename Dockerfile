# ========================================================
# STAGE 1: Dependency Compiler Build
# ========================================================
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system compilation packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements to leverage Docker caching layers
COPY requirements.txt .

# Install dependencies into a localized wheel folder
RUN pip install --no-cache-dir --user -r requirements.txt

# ========================================================
# STAGE 2: Lightweight Production Runner
# ========================================================
FROM python:3.12-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

# Install standard runtime shared library dependencies (libglib and openGL packages for OpenCV runs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed site-packages wheels from Builder Stage
COPY --from=builder /root/.local /root/.local

# Copy entire application source code
COPY . .

EXPOSE 8000

# Launch ASGI uvicorn server mapping standard ingress points
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
