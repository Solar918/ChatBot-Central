FROM python:3.10-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose application port
EXPOSE 8005

# Default environment variables
ENV FLASK_ENV=production \
    PORT=8005

# Launch the Flask app
CMD ["python", "app.py"]
