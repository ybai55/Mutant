FROM --platform=linux/amd64 python:3.10

#RUN apt-get update -qq
#RUN apt-get install python3.10 python3-pip -y --no-install-recommends && rm -rf /var/lib/apt/lists_/*

WORKDIR /mutant-server

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./mutant_server /mutant-server/mutant_server

EXPOSE 8000

CMD ["uvicorn", "mutant_server.api:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]