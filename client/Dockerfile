# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the client code and proto files
COPY client.py ./
COPY protos/crud.proto ./protos/

# Generate Python code from proto file
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/crud.proto

# Run the client
CMD ["python", "client.py"]