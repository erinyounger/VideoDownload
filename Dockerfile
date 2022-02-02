FROM markadams/chromium-xvfb-py3:latest

USER root

RUN mkdir /home/xvideo/

COPY . /home/xvideo/
ADD bin/sources.list /etc/apt/sources.list

RUN set -x \
    && apt update && apt -y install ffmpeg \
    && cd /home/xvideo/ && pip3 install -r ./requirements.txt --index-url=https://mirrors.aliyun.com/pypi/simple/


WORKDIR /home/xvideo
