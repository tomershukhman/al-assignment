FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management
RUN pip install uv

# Copy dependency files from root
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Copy backend code
COPY backend ./backend/

# Copy seed data
COPY seed_data.json ./

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Set Python path
ENV PYTHONPATH=/app

# Initialize database and start server
CMD ["sh", "-c", "python -m backend.init_db && uvicorn backend.main:app --host 0.0.0.0 --port 8000"]

