# Используем официальный Python 3.11 slim
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /src

# Копируем файлы зависимостей и устанавливаем их
COPY requirements.txt .

# Устанавливаем зависимости проекта
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё содержимое проекта в контейнер
COPY . .

# Запускаем бота
CMD ["python", "src/main.py"]
