FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY wsgi.py .
COPY src/ ./src/
COPY static/ ./static/
COPY templates/ ./templates/
COPY assets/ ./assets/
COPY version.json .

# Create data directory for database
RUN mkdir -p data

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "wsgi:app", "--host", "0.0.0.0", "--port", "8000"]
