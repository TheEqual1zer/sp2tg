FROM python:3.12.4-alpine

WORKDIR /app

RUN apk add --no-cache ffmpeg

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
