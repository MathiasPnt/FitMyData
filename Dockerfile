FROM python:3.9-slim

WORKDIR /workspace

ADD packages.txt .

RUN apt update -y && xargs apt-get install -y <packages.txt

ADD requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

ADD . .

ENTRYPOINT ["streamlit", "run", "app.py"]
