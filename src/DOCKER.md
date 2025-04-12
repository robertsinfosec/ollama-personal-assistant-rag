# Docker Guide for Ollama Personal Assistant

This guide explains how to build, run, and interact with the Ollama Personal Assistant using Docker.

## Table of Contents

- [Docker Guide for Ollama Personal Assistant](#docker-guide-for-ollama-personal-assistant)
  - [Table of Contents](#table-of-contents)
  - [Building the Docker Image](#building-the-docker-image)
    - [Basic Build](#basic-build)
    - [Versioning](#versioning)
  - [Running the Container](#running-the-container)
    - [Basic Usage](#basic-usage)
    - [Configuration Options](#configuration-options)
  - [Volume Mounting for Data Management](#volume-mounting-for-data-management)
  - [Container Management Commands](#container-management-commands)
    - [Viewing Logs](#viewing-logs)
    - [Stopping and Starting](#stopping-and-starting)
    - [Removing Containers](#removing-containers)
  - [Interacting with the Container](#interacting-with-the-container)
    - [Using the Interactive CLI](#using-the-interactive-cli)
    - [Regenerating Personal Information](#regenerating-personal-information)
  - [Example Workflow](#example-workflow)

## Building the Docker Image

### Basic Build

To build the Docker image from the Dockerfile in the project:

```bash
# From the repository root directory
cd src
docker build -t ollama-assistant:latest .
```

This will create an image named `ollama-assistant` with the tag `latest`.

### Versioning

For version control and deployment, it's recommended to tag your images with specific versions:

```bash
# Build with a version tag
docker build -t ollama-assistant:1.0.0 .

# Add latest tag to the same image
docker tag ollama-assistant:1.0.0 ollama-assistant:latest
```

For automated CI/CD pipelines, you might want to include a build timestamp:

```bash
# Build with a timestamp tag
docker build -t ollama-assistant:$(date +%Y%m%d-%H%M%S) .
```

## Running the Container

### Basic Usage

To run the container with default settings:

```bash
docker run -d \
  --name oliver-assistant \
  -p 8901:8901 \
  ollama-assistant:latest
```

This will:
- Start the container in detached mode (`-d`)
- Name it `oliver-assistant` for easy reference
- Map port 8901 from the container to port 8901 on your host
- Use the latest version of the image

### Configuration Options

You can customize the container using environment variables:

```bash
docker run -d \
  --name oliver-assistant \
  -p 9000:9000 \
  -e HOST=0.0.0.0 \
  -e PORT=9000 \
  -e OLLAMA_API_HOST=http://your-ollama-server:11434 \
  ollama-assistant:latest
```

> [!NOTE]
> When running the container on the same host as your Ollama server, use `host.docker.internal` instead of `localhost` in the `OLLAMA_API_HOST` variable to access the host machine from within the container.

## Volume Mounting for Data Management

To customize and update your personal information without rebuilding the container, you can mount the data directory as a volume:

```bash
docker run -d \
  --name oliver-assistant \
  -p 8901:8901 \
  -v ./my-custom-data:/app/data \
  ollama-assistant:latest
```

This allows you to:
1. Modify YAML data files directly on your host
2. Regenerate the personal information markdown as needed
3. Persist your data between container restarts

> [!IMPORTANT]
> Ensure the mounted directory contains the proper structure with `static/`, `dynamic/`, and `templates/` subdirectories.

## Container Management Commands

### Viewing Logs

To see the logs from your running container in real-time:

```bash
docker logs oliver-assistant -f
```

The `-f` flag follows the log output, so you'll see new logs as they're generated.

### Stopping and Starting

```bash
# Stop the container
docker stop oliver-assistant

# Start it again
docker start oliver-assistant

# Restart the container
docker restart oliver-assistant
```

### Removing Containers

```bash
# Remove a stopped container
docker rm oliver-assistant

# Force remove a running container
docker rm -f oliver-assistant
```

## Interacting with the Container

### Using the Interactive CLI

You can access the interactive CLI interface inside the running container:

```bash
docker exec -it oliver-assistant python main.py interactive
```

Add the `--verbose` flag to see retrieved context:

```bash
docker exec -it oliver-assistant python main.py interactive --verbose
```

### Regenerating Personal Information

After updating YAML files in your mounted volume, regenerate the personal information markdown:

```bash
docker exec oliver-assistant python main.py generate
```

Then reload the vector store to apply the changes without restarting:

```bash
# Using curl to the API endpoint
curl -X POST "http://localhost:8901/reload"

# Or access the interactive CLI and use the /reload command
docker exec -it oliver-assistant python main.py interactive
```

## Example Workflow

Here's a complete example workflow for setting up and using the containerized assistant:

```bash
# Build the image
docker build -t ollama-assistant:latest .

# Run the container with a mounted volume
mkdir -p ./my-data
cp -r ./data/* ./my-data/
docker run -d --name oliver-assistant -p 8901:8901 -v $PWD/my-data:/app/data ollama-assistant:latest

# Modify some personal information
nano ./my-data/static/owner.yaml

# Regenerate the markdown
docker exec oliver-assistant python main.py generate

# Reload the vector store
curl -X POST "http://localhost:8901/reload"

# Test with the interactive CLI
docker exec -it oliver-assistant python main.py interactive
```

> [!TIP]
> For production use, consider using Docker Compose to manage the Ollama server and this personal assistant together. This simplifies network configuration and service management.