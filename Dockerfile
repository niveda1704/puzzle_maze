FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variable for Flask
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Expose port (Render sets $PORT dynamically, but 5000 is default)
EXPOSE 5000

# Run the application
CMD gunicorn --bind 0.0.0.0:$PORT app:app
