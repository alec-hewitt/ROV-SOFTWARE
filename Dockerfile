# Use Debian slim but optimize for size
FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    i2c-tools \
    python3-dev \
    gcc \
    g++ \
    python3-smbus \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logging directory
RUN mkdir -p logging

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose the TCP port used for surface communication
EXPOSE 65432

# Run as root for hardware access (required for I2C devices)
# Note: Hardware access requires root privileges

# Health check - check if Python process is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ps aux | grep "python rov.py" | grep -v grep || exit 1

# Default command
CMD ["python", "rov.py"]
