FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY authentication/main.py ./main.py
COPY authentication/configuration.py ./configuration.py
COPY authentication/models.py ./models.py
COPY requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt
ENV PYTHONPATH="/opt/src/authentication"

ENTRYPOINT ["python", "./main.py"]
