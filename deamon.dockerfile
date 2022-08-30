FROM python:3

RUN mkdir -p /opt/src/shop
WORKDIR /opt/src/shop

COPY shop/daemon.py ./application.py
COPY shop/configuration.py ./configuration.py
COPY shop/models.py ./models.py
COPY shop/decorator.py ./decorator.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

# project root folder
ENV PYTHONPATH="/opt/src/shop"

ENTRYPOINT ["python", "./application.py"]