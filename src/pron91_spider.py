# -*- coding:utf-8 -*-
import os.path
import re
import platform
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
try:
    from xvfbwrapper import Xvfb
except:
    pass

from http_helper import proxies
from log import logger

class Pron91Spider:
    def __init__(self, index_url, tmp_dir=None):
        self.tmp_dir = tmp_dir
        self.index_url = index_url
        self.video_list = list()
        self.base_url = 'http://cdn77.91p49.com'
        self.m3u8_base_url = self.base_url+"/m3u8/{0}/{0}.m3u8"
        self.ts_base_url = self.base_url+"/m3u8/{0}/"
        self.dispaly = None
        self.driver = None
        self.init_dirver()

    def init_dirver(self):
        chrom_options = webdriver.ChromeOptions()
        if platform.system() == "Windows":
            # chrome version: 95
            chromedriver = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bin', 'chromedriver.exe')
        else:
            self.dispaly = Xvfb(width=1980, height=1280)
            self.dispaly.start()
            chrom_options.add_argument("--no-sandbox")
            chromedriver = ChromeDriverManager(url="https://npm.taobao.org/mirrors/chromedriver/",
                                               latest_release_url="https://registry.npmmirror.com/-/binary/chromedriver/LATEST_RELEASE").install()
        self.driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chrom_options)

    def request_bs4(self, url, request=False):
        if request:
            response = requests.get(url, proxies=proxies)
            if response.ok:
                return BeautifulSoup(response.content, "lxml")
            else:
                raise Exception("Request [{}] fail.\n{}".format(url, response.content))
        else:
            self.driver.get(url)
            soup_resource = BeautifulSoup(self.driver.page_source, "lxml")
            # logger.info("soup_resource: {}".format(soup_resource))
            # self.driver.close()
            return soup_resource

    def is_machine(self, url):
        soup = self.request_bs4(url)
        fonts = soup.find_all("font")
        res = list(map(lambda text: re.search("请点击以下链接访问，以验证你不是机器人！", str(text)), fonts))
        if any(res):
            # driver = webdriver.Chrome()
            self.driver.get(url)
            check_button = self.driver.find_element_by_tag_name('a')
            check_button.click()
            time.sleep(5)
            soup_resource = BeautifulSoup(self.driver.page_source, "lxml")
            return soup_resource
        else:
            return soup

    def find_video_info(self, url):
        soup = self.is_machine(url)
        videos = soup.find_all(attrs={'class': 'thumb-overlay'})
        for child in videos:
            info = dict()
            matcher = re.search(r'playvthumb_(\d+)', child.attrs.get('id'))
            if not matcher:
                continue
            info["id"] = matcher.groups()[0]
            logger.info("find video ID: {}".format(info["id"]))
            url = child.parent.attrs['href']
            for chd in child.children:
                if isinstance(chd, str):
                    continue
                if chd.attrs.get("class") and isinstance(chd.attrs.get("class"), list):
                    if chd.attrs.get("class")[0] == 'hd-text-icon':
                        info["hd"] = chd.text
                    if chd.attrs.get("class")[0] == "duration":
                        info["duration"] = chd.text
                    if chd.attrs.get("class")[0] == 'img-responsive':
                        info["img_url"] = chd.attrs.get("src")
            # self.get_video_detail(url)
            info["m3u8_url"] = self.m3u8_base_url.format(info["id"])
            info["ts_base_url"] = self.ts_base_url.format(info["id"])
            self.video_list.append(info)
            logger.info(url, info)

    def get_video_detail(self, url):
        # TODO 详细播放地址
        soup = self.request_bs4(url)
        div_info = soup.find(attrs={"class": "video-container"})
        matcher = re.search(r"strencode2\(\"(\S+)\"\)", str(div_info.next_element.next_element))
        logger.info(div_info)
