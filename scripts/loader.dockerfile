FROM python:3.9-slim

# تحديث وتثبيت التبعيات
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مجلد العمل
WORKDIR /app

# نسخ الملفات
COPY . /app

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# الأمر الافتراضي
CMD ["python", "scraper.py"]