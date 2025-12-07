FROM python:3.13-alpine

WORKDIR /app

COPY ./common /app/common

RUN pip install -e /app/common

COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]