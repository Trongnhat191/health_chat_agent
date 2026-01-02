FROM python:3.10-slim

WORKDIR /app

# Cài đặt các dependencies hệ thống nếu cần (ví dụ cho build tools)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Mở cổng cho API Agent
EXPOSE 8001

# Chạy server
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]