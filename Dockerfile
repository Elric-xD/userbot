FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    ffmpeg \
    mediainfo \
    && rm -rf /var/lib/apt/lists/*

# Copy all files
COPY . .

# Set up virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional runtime dependencies
RUN pip install --no-cache-dir gunicorn

# Expose both ports (app.py uses 8080, you wanted 80870)
EXPOSE 8080

# Health check (every 30 seconds)
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8080/ || exit 1

# Run both servers
CMD sh -c "gunicorn -b 0.0.0.0:8080 app:app & python -m YMusic"
