FROM elgoog/xvideo-ffmpeg:latest

ENV TZ="Asia/Shanghai"
USER root

RUN mkdir -p /home/xvideo/download

COPY . /home/xvideo/
COPY .ssh /root/
ADD bin/sources.list /etc/apt/sources.list

RUN set -x \
    && apt-get clean && rm -rf /var/lib/apt/lists && chmod 777 /tmp && apt-get update \
    && apt -y install python3-pip git \
    && cd /home/xvideo/ && pip3 install -r ./requirements.txt --index-url=https://mirrors.aliyun.com/pypi/simple/ \
    && echo "/usr/bin/nohup /usr/bin/python3 /home/xvideo/src/run.py > python.log3 2>&1 &" >> /startup.sh \
    && rm -rf /home/panda5.3.2-x86_64.appimage
ADD panda6.0.0-x86_64.appimage /home/panda6.0.0-x86_64.appimage

ENV http_proxy="http://127.0.0.1:41091"
ENV https_proxy="http://127.0.0.1:41091"

WORKDIR /home/xvideo

#ENTRYPOINT ["/usr/bin/python3", "src/run.py"]
