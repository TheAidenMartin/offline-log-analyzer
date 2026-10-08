# Use a lightweight Python 3.11 image
FROM python:3.11-slim

WORKDIR /app

# Install the frozen dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY . .

# Open port 8000 and start the API server
EXPOSE 8000
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]