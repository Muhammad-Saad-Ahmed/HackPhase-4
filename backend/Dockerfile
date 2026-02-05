FROM python:3.11-slim

# Set environment variables for Hugging Face Spaces
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=7860

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install uv for dependency management
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml uv.lock ./

# Copy source code (before install — setuptools needs src/ to build package)
COPY src ./src

# Install dependencies + project using uv
RUN uv pip install --system --compile-bytecode .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port required by Hugging Face Spaces
EXPOSE 7860

# Health check adapted for Hugging Face Spaces
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run the application with Hugging Face Spaces port
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]