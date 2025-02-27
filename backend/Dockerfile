# Use a lightweight Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy files into the container
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./

# Load environment variables
ENV OPENROUTER_API_KEY=${OPENROUTER_API_KEY}

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]