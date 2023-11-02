# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python file into the container
COPY main.py /app/main.py

# Install Flask
RUN pip3 install Flask

# Make port 80 available to the world outside this container
EXPOSE 80

# Run the Flask application
CMD ["python3", "main.py"]
