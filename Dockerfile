# ---- build stage ----
FROM python:3.11-slim

# 環境変数
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Streamlit のヘッドレス実行
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.headless=true", "--server.address=0.0.0.0"]