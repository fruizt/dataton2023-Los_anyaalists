# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the project files into the Docker image
COPY . .

# Install your project and dependencies
RUN pip install --no-cache-dir ./src/project

# Run solution.py when the container launches
CMD ["python3", "./src/solution.py"]