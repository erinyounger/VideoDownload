# -*- coding:utf-8 -*-
import os
import time
import traceback
from urllib.parse import urlencode
from m3u8_download import M3u8Download
from pron91_spider import Pron91Spider

from log import logger

DOWNLOAD_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "download")

BACK_UP_DIRS = [DOWNLOAD_BASE_DIR]


def download_91pron(category="hot", month=None, page_num=None):
    """
    :param category:
            首页：index
            当前最热：hot
            本月最热：top
            本月收藏：tf
            收藏最多：mf
            最近加精：rf
            本月讨论：md
            高清：hd
    :param page_num: 遍历几页，None表示当前页
    :param month:
            当月：None
            上月：-1
    :return:
    """
    url_params = {"viewtype": "basic", "category": category}
    url_params.update({"m": month}) if month else None
    url = "https://www.91porn.com/v.php?" + urlencode(url_params)

    download_urls = list()
    if category == "index":
        download_urls.append("http://www.91porn.com/index.php")
    elif page_num is not None:
        for page in range(1, page_num):
            download_urls.append("{}&page={}".format(url, page))
    else:
        download_urls.append(url)

    for url in download_urls:
        pron = Pron91Spider(url, DOWNLOAD_BASE_DIR)
        logger.info("URL: {}".format(pron.index_url))
        pron.find_video_info(pron.index_url)
        for video in pron.video_list:
            _vide_name = "{}.mp4".format(video["id"])
            spider = M3u8Download(info=video)
            is_exist = False
            for _dir in BACK_UP_DIRS:
                if spider.is_downloaded(_dir, _vide_name):
                    is_exist = True
                    continue
            if not is_exist:
                download_dir = os.path.join(DOWNLOAD_BASE_DIR, time.strftime("%Y%m%d"))
                spider.set_download_path(download_dir)
                spider.execute(_vide_name)
        else:
            logger.error("No Video info: {}".format(pron.video_list))
        try:
            if pron.dispaly:
                pron.dispaly.stop()
            pron.driver.close()
        except Exception as ex:
            logger.error("Close webdriver fail.")


if __name__ == '__main__':
    # download video from 91pron
    page_num = 5
    while True:
        try:
            download_91pron(category="index")
            download_91pron(category="ori", page_num=page_num)
            download_91pron(category="rf", page_num=page_num)
            download_91pron(category="hot", page_num=page_num)
            download_91pron(category="top", page_num=page_num)
        except Exception as ex:
            logger.error("download fail.\n{}".format(traceback.format_exc()))
        finally:
            logger.info("Sleep Wait Next Download.")
            time.sleep(3600)
