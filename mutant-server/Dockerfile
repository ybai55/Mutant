FROM --platform=linux/amd64 python:3.10 AS mutant_server

#RUN apt-get update -qq
#RUN apt-get install python3.10 python3-pip -y --no-install-recommends && rm -rf /var/lib/apt/lists_/*

WORKDIR /mutant-server

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./mutant_server /mutant-server/mutant_server

EXPOSE 8000

CMD ["uvicorn", "mutant_server:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]

# Use a multi-stage build to layer in test dependencies without bloating server image
# https://docs.docker.com/build/building/multi-stage
# Note: requires passing --target to docker-build.
FROM mutant_server AS mutant_server_test

COPY ./requirements_dev.txt requirements_dev.txt
RUN pip install --no-cache-dir --upgrade -r requirements_dev.txt

CMD ["python", "-m", "pytest"]