FROM python:3.10-slim

WORKDIR /app

# Set environment variables with defaults that can be overridden
ENV HOST="0.0.0.0"
ENV PORT="8901"
ENV OLLAMA_API_HOST="http://host.docker.internal:11434"

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Generate the personal information markdown
RUN python main.py generate

# Create a volume mount point for easy updates to data files
VOLUME ["/app/data"]

# Expose the API port
EXPOSE 8901

# Run the API server with environment variable configuration
CMD python main.py api --host ${HOST} --port ${PORT}
