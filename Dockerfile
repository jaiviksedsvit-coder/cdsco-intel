FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files and production database
COPY cdsco_approvals.db .
COPY app.py .
COPY public/ public/

# Default environment variables
ENV PORT=8000
ENV HOST=0.0.0.0
ENV DEBUG=false

EXPOSE 8000

CMD ["python", "app.py"]
