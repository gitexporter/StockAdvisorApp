FROM python:3.9-slim

# Set working directory
WORKDIR /app/StockAdvisorApp

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Add the application directory to PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Expose the port the app runs on
EXPOSE 8000

# Update the command to use the correct module path
CMD ["uvicorn", "agents.main:app", "--host", "0.0.0.0", "--port", "8000"]