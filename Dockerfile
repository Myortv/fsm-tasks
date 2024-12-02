FROM python:3.11-slim


RUN apt-get update
RUN apt-get install -y git

WORKDIR /app

COPY req.txt .

RUN pip install -r req.txt


COPY . /app



EXPOSE 8000

CMD ["python", "src/main.py"]
