# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set environment variables to avoid Python writing pyc files and buffering output
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=2.1.1

# Set the working directory in the container
WORKDIR /app

# Install Poetry
RUN pip install poetry==$POETRY_VERSION

# Copy pyproject.toml and poetry.lock to install dependencies
COPY pyproject.toml poetry.lock* /app/

# Install dependencies via Poetry
RUN poetry install --no-interaction --no-ansi

# Copy the rest of your application code to the container
COPY . /app/

# Expose the port the app will run on
EXPOSE 8000

# Command to run your FastAPI app with uvicorn
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
