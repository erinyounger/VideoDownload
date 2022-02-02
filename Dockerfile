FROM elgoog/xvideo-ffmpeg:latest

ENV TZ="Asia/Shanghai"
USER root

RUN mkdir -p /home/xvideo/download

COPY . /home/xvideo/
ADD bin/sources.list /etc/apt/sources.list

RUN set -x \
#    && apt update && apt -y install ffmpeg \
    && cd /home/xvideo/ && pip3 install -r ./requirements.txt --index-url=https://mirrors.aliyun.com/pypi/simple/

ENV http_proxy="http://192.168.3.6:41091"
ENV https_proxy="http://192.168.3.6:41091"

WORKDIR /home/xvideo

ENTRYPOINT ["/usr/bin/python3", "src/run.py"]
