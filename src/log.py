# -*- coding:utf-8 -*-
import os
import logging

if not os.path.exists("logs"):
    os.makedirs("logs")

logger = logging.getLogger("Spider")
ch_handler = logging.StreamHandler()
fh_handler = logging.FileHandler('logs/xvideo.log')

formatter = logging.Formatter('[%(asctime)s][%(name)-4s][%(levelname)-4s] > %(message)s')
ch_handler.setFormatter(formatter)
fh_handler.setFormatter(formatter)

logger.addHandler(ch_handler)
logger.addHandler(fh_handler)
logger.setLevel(logging.INFO)
