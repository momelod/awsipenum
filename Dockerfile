FROM python:3.10.8

COPY . .

ENV AWS_DEFAULT_REGION=us-east-1

RUN pip3 install .

ENTRYPOINT ["/usr/local/bin/awsipenum"]
