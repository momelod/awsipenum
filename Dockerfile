FROM python:3.10.8

ENV AWS_DEFAULT_REGION=us-east-1

RUN pip3 install awsipenum --user

ENTRYPOINT ["/root/.local/bin/awsipenum"]
