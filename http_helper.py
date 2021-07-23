import requests
import time
import threading


def download_file(save_path, url, text=False, retry=10):
    while retry:
        try:
            response = requests.get(url)
            if response.ok:
                if text:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(response.text)
                else:
                    with open(save_path, "wb") as f:
                        f.write(response.content)
                print("Download [{}] Success. thread:{}".format(save_path, threading.current_thread().name))
                return
        except:
            print("ERROR count:{0}: Request {1} fail. thread:{2}".format(10 - retry, url,
                                                                         threading.current_thread().name))
            retry -= 1
            time.sleep(5)
            continue
