# Use the official lightweight Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose the port your FastAPI app runs on
EXPOSE 8000

# Run the FastAPI app (adjust path to main:app)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]