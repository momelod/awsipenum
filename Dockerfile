FROM python:3.10.8

USER nobody

RUN pip3 install awsipenum

CMD awsipenum
