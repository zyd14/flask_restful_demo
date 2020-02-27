FROM python:3.8.2-slim

WORKDIR /

COPY src /src
COPY main.py .
COPY static /static
COPY dockerrequirements.txt .

RUN pip install --upgrade pip
RUN pip install -r /dockerrequirements.txt

ENTRYPOINT ["python", "main.py"]
