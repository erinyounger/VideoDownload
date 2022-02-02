FROM markadams/chromium-xvfb-py3:latest

USER root

RUN mkdir -p /home/xvideo/download

COPY . /home/xvideo/
ADD bin/sources.list /etc/apt/sources.list

ENV http_proxy="http://192.168.3.6:41091"
ENV https_proxy="http://192.168.3.6:41091"

RUN set -x \
    && apt update && apt -y install ffmpeg \
    && cd /home/xvideo/ && pip3 install -r ./requirements.txt --index-url=https://mirrors.aliyun.com/pypi/simple/

WORKDIR /home/xvideo

#ENTRYPOINT ["/usr/bin/python3", "src/run.py"]
