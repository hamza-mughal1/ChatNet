# Use the official Python image from the Docker Hub
FROM python:3.11

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables (use defaults or adjust as needed)
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DB=postgresql 
ENV DB_PASSWORD=jKCsgcjbVthpaPnwCMUUddEGCLiWyrAb 
ENV DB_HOST=junction.proxy.rlwy.net 
ENV DB_PORT=44205 
ENV DB_NAME=railway 
ENV SECRET_KEY=77cfbtdl757pu7n526qng21g4ib3?2yy8n9dvj3arn4x52j183jyjunlrxcds6r6 
ENV ALGORITHM=HS256 
ENV ACCESS_TOKEN_EXPIRE_MINUTES=30 
ENV REFRESH_TOKEN_EXPIRE_MINUTES=43200 
ENV PATH="/opt/venv/bin:$PATH"

# Expose the port the app runs on
EXPOSE 8000

# Command to run the app
CMD python3 app.py
