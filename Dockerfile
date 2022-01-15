FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

# Local Redis Config. redis isn't accessible outside local network
ENV ENDPOINT=rd
ENV USER=penguinrage
ENV SECRET=K$jyLjd59tT#bV

CMD [ "python3", "app.py"]
