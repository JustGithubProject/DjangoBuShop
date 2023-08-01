# Используем базовый образ Python
FROM python:3.9

WORKDIR /app

# Копируем зависимости файла requirements.txt и устанавливаем их
COPY requirements.txt /app/
RUN pip install -r requirements.txt


# Копируем все содержимое проекта в рабочую директорию образа
COPY . /app/



