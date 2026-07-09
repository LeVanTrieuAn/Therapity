FROM public.ecr.aws/docker/library/python:3.11-slim
WORKDIR /app

# Cài đặt các thư viện cần thiết
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn (bao gồm cả backend và frontend)
COPY . .

# Đảm bảo các thư mục cần thiết tồn tại và có quyền ghi
RUN mkdir -p /app/database && chmod 777 /app/database

# Mở các cổng cần thiết
EXPOSE 8000
EXPOSE 8501

# Biến môi trường
ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

# Chạy server
CMD ["python", "backend/main.py"]
