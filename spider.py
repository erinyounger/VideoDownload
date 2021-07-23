import os
import re
import shutil
import datetime
import queue
import time

import requests
import threading
from bs4 import BeautifulSoup


class PronSpider:
    def __init__(self, index_url):
        self.index_url = index_url
        self.video_list = list()

    def request_bs4(self, url):
        proxies = {
            "http": "http://127.0.0.1:41091",
            "https": "http://127.0.0.1:41091",
        }
        response = requests.get(url, proxies=proxies)
        if response.ok:
            return BeautifulSoup(response.content, "lxml")
        else:
            raise Exception("Request [{}] fail.".format(url))

    def find_video_info(self, url):
        soup = self.request_bs4(url)
        videos = soup.find_all(attrs={'class': 'thumb-overlay'})
        for child in videos:
            info = dict()
            matcher = re.search('playvthumb_(\d+)', child.attrs['id'])
            info["id"] = matcher.groups()[0]
            url = child.parent.attrs['href']
            for chd in child.children:
                if isinstance(chd, str):
                    continue
                if chd.attrs.get("class") and isinstance(chd.attrs.get("class"), list):
                    if chd.attrs.get("class")[0] == 'hd-text-icon':
                        info["hd"] = chd.text
                    if chd.attrs.get("class")[0] == "duration":
                        info["duration"] = chd.text
            # self.get_video_detail(url)
            self.video_list.append(info)
            print(url, info)

    def get_video_detail(self, url):
        soup = self.request_bs4(url)
        div_info = soup.find(attrs={"class": "video-container"})
        matcher = re.search(r"strencode2\(\"(\S+)\"\)", str(div_info.next_element.next_element))
        print(div_info)


class M3u8Download:
    def __init__(self, m3u8_file, ts_base_url, work_dir=None):
        if not work_dir:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.base_dir = work_dir
        self.ts_pool = list()
        self.ts_base_url = ts_base_url
        self.m3u8_file = m3u8_file
        self.download_path = os.path.join(self.base_dir, "var")
        self.template_dir = os.path.join(self.base_dir, "var", self.now_str)
        self.download_queue = queue.Queue()
        self.create_download_thread(self.download_queue)

    def create_download_thread(self, q, thread_num=10):
        for i in range(thread_num):
            worker = threading.Thread(name="download_thread-{}".format(i),
                                      target=self.download, args=(q,), daemon=True)
            worker.start()

    def download(self, q):
        while True:
            task = q.get()
            self.download_file(task[0], task[1])
            time.sleep(5)
            q.task_done()

    def set_download_path(self, path):
        self.download_path = path

    @property
    def now_str(self):
        return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    def parse_m3u8(self):
        m3u8_path = self.m3u8_file
        if re.search("http", self.m3u8_file):
            if not os.path.exists(self.template_dir):
                os.mkdir(self.template_dir)
            m3u8_path = os.path.join(self.template_dir, self.now_str + ".m3u8")
            self.download_file(m3u8_path, self.m3u8_file, text=True)

        with open(m3u8_path, 'r') as f:
            line = "1"
            while line:
                line = f.readline().strip()
                ts_matcher = re.search(r"^(\d+\.ts)$", line)
                if not ts_matcher:
                    continue
                self.ts_pool.append(ts_matcher.groups()[0])
        print("TS_POOL: {}".format(self.ts_pool))

    def download_ts_file(self):
        for ts in self.ts_pool:
            ts_path = os.path.join(self.template_dir, ts)
            ts_url = self.ts_base_url + ts
            self.download_queue.put((ts_path, ts_url))
        self.download_queue.join()

    def is_downloaded(self, target_name):
        return os.path.exists(os.path.join(self.download_path, target_name))

    def combine_ts_file(self, target_name):
        target_path = os.path.join(self.download_path, target_name)
        with open(target_path, "ab") as tg_f:
            for ts in self.ts_pool:
                ts_path = os.path.join(self.template_dir, ts)
                with open(ts_path, "rb") as ts_f:
                    content = ts_f.read()
                tg_f.write(content)
        print("Combined TS file TO [{}]".format(target_path))

    def execute(self, target_name):
        if self.is_downloaded(target_name):
            print("Worming: already downlod: {}".format(target_name))
            return
        self.parse_m3u8()
        self.download_ts_file()
        self.combine_ts_file(target_name)
        self.clear()

    def clear(self):
        shutil.rmtree(self.template_dir)

    @staticmethod
    def download_file(file_path, url, text=False, retry=10):
        while retry:
            try:
                response = requests.get(url)
                if response.ok:
                    if text:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(response.text)
                    else:
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                    print("Download [{}] Success. thread:{}".format(file_path, threading.current_thread().name))
                    return
            except Exception as ex:
                print("ERROR count:{0}: Request {1} fail. thread:{2}".format(10-retry, url, threading.current_thread().name))
                retry -= 1
                time.sleep(5)
                continue


if __name__ == '__main__':
    for page in range(1, 2):
        # pron = PronSpider(index_url="http://www.91porn.com/v.php?category=rf&viewtype=basic&page={}".format(page))
        pron = PronSpider(index_url="http://www.91porn.com/v.php?category=hd&viewtype=basic")
        pron.find_video_info(pron.index_url)
        for video in pron.video_list:
            vide_id = video["id"]
            spider = M3u8Download(m3u8_file="https://fdc.91p49.com/m3u8/{0}/{0}.m3u8".format(vide_id),
                                  ts_base_url="https://cdn.91p07.com/m3u8/{}/".format(vide_id))
            spider.execute("{}.mp4".format(vide_id))
