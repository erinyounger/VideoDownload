import re
import requests
from bs4 import BeautifulSoup


class Pron91Spider:
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
            matcher = re.search(r'playvthumb_(\d+)', child.attrs['id'])
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
