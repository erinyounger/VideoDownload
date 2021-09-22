import re
import os
import time
import shutil
import datetime
import subprocess
from download_pool import DownloadPool
from http_helper import download_file
from log import logger


class M3u8Download:
    def __init__(self, info, work_dir=None):
        if not work_dir:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.base_dir = work_dir
        self.ts_pool = list()
        self.ts_base_url = info.get("ts_base_url")
        self.m3u8_file = info.get("m3u8_url")
        self.img_url = info.get("img_url")
        self.img_path = None
        self.video_id = info.get("id")
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

            if self.img_url:
                self.img_path = os.path.join(self.template_dir, self.video_id+".jpg")
                download_file(self.img_path, self.img_url)

        with open(m3u8_path, 'r') as f:
            line = "1"
            while line:
                line = f.readline().strip()
                ts_matcher = re.search(r"^(\d+\.ts)$", line)
                if not ts_matcher:
                    continue
                self.ts_pool.append(ts_matcher.groups()[0])
        logger.info("TS_POOL: {}".format(self.ts_pool))

    def download_ts_file(self):
        task_list = list()
        for ts in self.ts_pool:
            ts_path = os.path.join(self.template_dir, ts)
            ts_url = self.ts_base_url + ts
            task_list.append((download_file, ts_path, ts_url))
        d_pool = DownloadPool()
        d_pool.start(task_list)
        d_pool.join()

    def is_downloaded(self, base_dir, target_name):
        download_dir = os.path.join(base_dir, time.strftime("%Y%m%d"))
        for root, ds, fs in os.walk(base_dir):
            for f in fs:
                if re.match(target_name, f):
                    logger.info("Worming: already download: {}".format(target_name))
                    return True
        self.set_download_path(download_dir)
        return False

    def combine_ts_file(self, target_name):
        target_path = os.path.join(self.download_path, target_name)
        with open(target_path, "ab") as tg_f:
            for ts in self.ts_pool:
                ts_path = os.path.join(self.template_dir, ts)
                with open(ts_path, "rb") as ts_f:
                    content = ts_f.read()
                tg_f.write(content)
        out_put_path = os.path.join(self.download_path, "img_"+target_name)
        self.attach_img(target_path, self.img_path, out_put_path)
        os.remove(os.path.join(self.download_path, target_name))
        os.rename(out_put_path, target_path)
        logger.info("Combined TS file TO [{}]".format(target_path))

    def attach_img(self, mp4_path, img_path, out_path):
        cmd = "D:/04_PyCode/tools_bin/ffmpeg.exe -i {0} -i {1} -map 1 -map 0 -c copy -disposition:0 attached_pic {2}".format(
            mp4_path, img_path, out_path
        )
        sub = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        sub.wait()

    def execute(self, target_name):
        self.parse_m3u8()
        self.download_ts_file()
        self.combine_ts_file(target_name)
        self.clear()

    def clear(self):
        shutil.rmtree(self.template_dir)
