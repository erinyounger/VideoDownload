import requests
import time
import threading
from log import logger


def download_file(save_path, url, text=False, retry=10):
    while retry:
        try:
            header = {"Accept-Encoding": "identity"}
            start = time.time()
            response = requests.get(url, headers=header)
            end = time.time()
            total_length = float(response.headers.get('Content-length', 1))
            used_time = end - start
            speed = total_length / 1024 / 1024 / used_time
            if response.ok:
                if text:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(response.text)
                else:
                    with open(save_path, "wb") as f:
                        f.write(response.content)
                logger.info("Download Speed: {:.2f} M/S, Path: [{}] - thread:{}".format(
                    speed, save_path, threading.current_thread().name))
                return
        except Exception as ex:
            logger.error("ERROR count:{0}: Request {1} fail. thread:{2}".format(10 - retry, url,
                                                                                threading.current_thread().name))
            logger.exception(ex)
            retry -= 1
            time.sleep(5)
            continue
