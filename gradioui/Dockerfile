FROM python:3.10-slim

WORKDIR /app

# Copy requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code vào thư mục src trong container
COPY src/ .

# Gradio mặc định chạy port 7860
EXPOSE 7860

# Biến môi trường để Gradio lắng nghe mọi IP
ENV GRADIO_SERVER_NAME="0.0.0.0"

# Chạy ứng dụng
CMD ["python", "app.py"]