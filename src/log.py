# -*- coding:utf-8 -*-
import logging

logger = logging.getLogger("Spider")
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s][%(name)-4s][%(levelname)-4s] > %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
