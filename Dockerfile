# 1. Base image
FROM python:3.13-slim

# 2. Create a non-root user
RUN useradd --create-home --shell /bin/bash app

# 3. Set working directory
WORKDIR /app

# 4. Switch to non-root user
USER app

# 5. Copy requirements and install dependencies in user's local directory
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 6. Add user's local bin to PATH so installed CLI tools are available
ENV PATH=/home/app/.local/bin:$PATH

# 7. Copy application code
COPY . .

# 8. Set environment variables
EXPOSE 1001
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 9. Default command to run the application
CMD ["python", "run.py"]
