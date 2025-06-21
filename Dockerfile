FROM python:3.11-slim
# Set work directory
WORKDIR /app
# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy app source
COPY ./app ./app
COPY .env.example .env
# Expose FastAPI default port
EXPOSE 8000
# Command to run the app with hot reload (remove --reload for production)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]