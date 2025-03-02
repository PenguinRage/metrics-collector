# Pull base image for RPI
FROM python:3.9-slim-buster

WORKDIR /app
EXPOSE 8086

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD [ "python3", "app.py"]
