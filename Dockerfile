# Используем легкий официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости (если понадобятся для сборки)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем зависимости (это кэшируется)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код проекта (включая папки data/ и models/)
COPY . .

# Streamlit по умолчанию работает на порту 8501
EXPOSE 8501

# Запускаем приложение. 
# $PORT — это переменная окружения, которую автоматически передают Render и Railway.
# --server.headless=true отключает браузер, --server.address=0.0.0.0 открывает доступ извне.
CMD streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true