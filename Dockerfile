FROM python:3.11-slim

WORKDIR /app

# Kerakli paketlar va fontlarni o'rnatish
RUN apt-get update && apt-get install -y \
    fonts-noto-core \
    fonts-noto-color-emoji \
    fontconfig \
    libfreetype6-dev \
    libpng-dev \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# Matplotlib keshini tozalash
RUN rm -rf ~/.cache/matplotlib

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]