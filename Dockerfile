FROM python:3.10

#RUN apt-get update -qq
#RUN apt-get install python3.10 python3-pip -y --no-install-recommends && rm -rf /var/lib/apt/lists_/*

WORKDIR /mutant

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./ /

EXPOSE 8000

CMD ["uvicorn", "mutant.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers"]