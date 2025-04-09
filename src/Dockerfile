FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p data/templates data/generated data/static

# Copy template and static data (these should exist in your source)
COPY data/templates/personal_info_template.md.j2 data/templates/
COPY data/personal_info_static.yaml data/static/

# Generate the personal info
RUN python -m generation.personal_info

# Expose the API port
EXPOSE 8901

# Run the uvicorn server
CMD ["python", "main.py", "api", "--host", "0.0.0.0", "--port", "8901"]
