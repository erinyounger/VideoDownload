from m38u_download import M3u8Download
from pron91_spider import Pron91Spider

if __name__ == '__main__':
    DOWNLOAD_DIR = r"D:\04_PyCode\Download"
    for page in range(1, 5):
        pron = Pron91Spider(index_url="http://www.91porn.com/v.php?category=rf&viewtype=basic&page={}".format(page))
        # pron = Pron91Spider(index_url="http://www.91porn.com/index.php")
        pron.find_video_info(pron.index_url)
        for video in pron.video_list:
            vide_id = video["id"]
            spider = M3u8Download(m3u8_file="https://fdc.91p49.com/m3u8/{0}/{0}.m3u8".format(vide_id),
                                  ts_base_url="https://cdn.91p07.com/m3u8/{}/".format(vide_id))
            spider.set_download_path(DOWNLOAD_DIR)
            spider.execute("{}.mp4".format(vide_id))
