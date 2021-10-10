import os
from urllib.parse import urlencode
from m3u8_download import M3u8Download
from pron91_spider import Pron91Spider

from log import logger

DOWNLOAD_BASE_DIR = "D:/04_PyCode/Download"


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
        logger.info(f"URL: {pron.index_url}")
        pron.find_video_info(pron.index_url)
        for video in pron.video_list:
            _vide_name = "{}.mp4".format(video["id"])
            spider = M3u8Download(info=video)
            if spider.is_downloaded(DOWNLOAD_BASE_DIR, _vide_name):
                continue
            spider.execute(_vide_name)


if __name__ == '__main__':
    # download video from 91pron
    download_91pron(category="index")
    download_91pron(category="ori", page_num=3)
    download_91pron(category="rf", page_num=3)
    os.system("shutdown -s -t 10")
