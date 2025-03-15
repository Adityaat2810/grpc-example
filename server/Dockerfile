# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server code and proto files
COPY server.py database.py ./
COPY protos/crud.proto ./protos/

# Generate Python code from proto file
RUN python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/crud.proto

# Expose the gRPC port
EXPOSE 50051

# Run the server
CMD ["python", "server.py"]