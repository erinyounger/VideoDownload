import re
import os
import shutil
import datetime
from download_pool import DownloadPool
from http_helper import download_file


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
        self.template_dir = os.path.join(self.download_path, "template", self.now_str)

    def set_download_path(self, path):
        self.download_path = path
        self.template_dir = os.path.join(self.download_path, "template", self.now_str)

    @property
    def now_str(self):
        return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    def parse_m3u8(self):
        m3u8_path = self.m3u8_file
        if re.search("http", self.m3u8_file):
            if not os.path.exists(self.template_dir):
                os.makedirs(self.template_dir)
            m3u8_path = os.path.join(self.template_dir, self.now_str + ".m3u8")
            download_file(m3u8_path, self.m3u8_file, text=True)

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
        task_list = list()
        for ts in self.ts_pool:
            ts_path = os.path.join(self.template_dir, ts)
            ts_url = self.ts_base_url + ts
            task_list.append((download_file, ts_path, ts_url))
        d_pool = DownloadPool()
        d_pool.start(task_list)
        d_pool.join()

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
