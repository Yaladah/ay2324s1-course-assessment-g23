# Use an official Python runtime as a parent image
FROM python:3.11.5-alpine3.18

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

RUN pip install pika==1.3.2 && \
    pip install aio_pika

# Run your application
CMD ["python", "rmq_server.py"]
