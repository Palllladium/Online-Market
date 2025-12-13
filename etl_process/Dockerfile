FROM python:3.13-alpine

WORKDIR /app

RUN apk update && apk add --no-cache tzdata

COPY requirements.txt .
COPY ./common ./common

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV TZ=UTC

CMD ["python", "main.py"]
