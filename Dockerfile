# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Force rebuild to fix Streamlit version issue - 2026-02-10

# Install system dependencies needed for some Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with optimizations
# Install PyTorch CPU-only version (much smaller than CUDA version)
RUN pip install --no-cache-dir \
    torch==2.0.0+cpu \
    torchvision==0.15.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt && \
    # Remove unnecessary files to reduce image size
    find /usr/local/lib/python3.11 -name "*.pyc" -delete && \
    find /usr/local/lib/python3.11 -name "__pycache__" -type d -exec rm -rf {} + || true && \
    rm -rf /root/.cache/pip

# Copy the entire application
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--browser.serverAddress=0.0.0.0", "--browser.gatherUsageStats=false"]
