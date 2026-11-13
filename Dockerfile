FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY --chown=10001:10001 . .
USER 10001:10001
CMD ["python", "app.py", "--offline", "--output-dir", "/tmp/run"]
