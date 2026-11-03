FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" gunicorn pydantic
COPY main.py resistor_logic.py ./
COPY static ./static
EXPOSE 8000
# TOKEN_SECRET must be set at deploy time (same value on all containers)
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "--timeout", "30"]
