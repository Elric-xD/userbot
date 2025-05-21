FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    git \
    wget \
    ffmpeg \
    mediainfo \
    && rm -rf /var/lib/apt/lists/*
COPY . .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "-m", "YMusic"]
