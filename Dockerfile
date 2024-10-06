# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY ./app ./app
COPY main.py .
COPY ./app/models ./app/models
COPY ./app/core ./app/core
COPY ./app/services ./app/services

# Expose the port on which the service will run
EXPOSE 8100

# Run the FastAPI application with debugpy for debugging
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100", "--reload"]
