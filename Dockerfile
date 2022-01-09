FROM python:3.9-slim

ADD packages.txt .

RUN apt update -y && xargs apt-get install -y <packages.txt

ADD requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

ADD . .

ENTRYPOINT ["streamlit", "run", "app_FitMyData.py"]
