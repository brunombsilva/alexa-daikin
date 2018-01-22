FROM python:2.7-alpine

ENV DEBIAN_FRONTEND noninteractive
ENV TERM xterm

WORKDIR /daikin

ADD requirements.txt .

RUN apk --update add python py-pip openssl ca-certificates py-openssl wget
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base linux-headers \
  && pip install --upgrade pip \
  && pip install -r requirements.txt \
  && apk del build-dependencies

ADD . .

EXPOSE 8183

CMD ["./server.py"]
