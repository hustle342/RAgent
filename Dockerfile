# RAgent - Dockerfile
# Multi-stage build

FROM python:3.10-slim as base

WORKDIR /app

# Sistem paketleri
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodu
COPY . .

# Streamlit config
RUN mkdir -p ~/.streamlit && \
    echo "[client]" > ~/.streamlit/config.toml && \
    echo "headless = true" >> ~/.streamlit/config.toml && \
    echo "port = 8501" >> ~/.streamlit/config.toml && \
    echo "serverAddress = '0.0.0.0'" >> ~/.streamlit/config.toml

# Port açık
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Streamlit uygulamasını başlat
CMD ["streamlit", "run", "src/ui/app.py", "--logger.level=info"]
