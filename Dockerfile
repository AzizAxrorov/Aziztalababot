# Engil Python 3.9 tasviridan foydalanamiz
FROM python:3.9-slim

# Ishchi direktoriyani o'rnatamiz
WORKDIR /app

# requirements.txt faylini konteynerga ko'chiramiz
COPY requirements.txt .

# Kerakli Python paketlarini o'rnatamiz
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini konteynerga ko'chiramiz
COPY . .

# Botni ishga tushirish uchun buyruq
CMD ["python", "main.py"]
