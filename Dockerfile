# Start with an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application code into the container at /app
COPY ./main.py /app/main.py

# Make port 80 available to the world outside this container
# (FastAPI/Uvicorn will run on this port inside the container)
EXPOSE 80

# Define environment variables (optional, but good practice)
ENV MODULE_NAME="main"
ENV VARIABLE_NAME="app"
# Listen on all network interfaces within the container
ENV APP_HOST="0.0.0.0"
# Run Uvicorn on port 80 inside the container
ENV APP_PORT="80"

# Command to run the application using Uvicorn
# Note: We don't use --reload here as it's for development.
# We use --host 0.0.0.0 so it's accessible from outside the container.
# We use --port $APP_PORT to use the environment variable we set.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]