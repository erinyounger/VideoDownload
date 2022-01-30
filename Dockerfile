FROM markadams/chromium-xvfb-py3:latest

USER root

RUN mkdir /home/xvideo/

COPY . /home/xvideo/

RUN set -x \
    && cd /home/xvideo/ && pip install -r ./requirements.txt


WORKDIR /home/xvideo
