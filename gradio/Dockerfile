FROM python:3.10-slim

WORKDIR /app

# Copy requirements (bạn cần tạo file này cho gradio/agent)
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code cần thiết
COPY agent-service/ ./agent/
COPY prepare_data/embed/ ./embed/
COPY data/ ./data/
COPY gradio/ ./gradio/

# Thiết lập biến môi trường để Python tìm thấy module
ENV PYTHONPATH=/app

# Chạy Gradio app
CMD ["python", "gradio/src/app.py"]