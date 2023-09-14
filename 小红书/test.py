# -*- coding: utf-8 -*-
import requests
import execjs

from os import mkdir
from os.path import exists, join
import json
import re
import time
import random


web_session = "040069b00ae8bc58760a9fc2a4364b933ead66"
a1 = "18696795090bcxx2v97se815odmlgmpudftw54qqd50000140517"


# -------------------------
#          下载器
# -------------------------
class Downloader:
    def __init__(self):
        self.download_path = "data"
        if not exists(self.download_path):
            mkdir(self.download_path)

    def get_response(self, article_id):
        """
        发送请求
        :param article_id:
        :return:
        """
        params = {
            "source_note_id": article_id
        }

        url = "https://edith.xiaohongshu.com/api/sns/web/v1/feed"
        api = "/api/sns/web/v1/feed"
        xs = get_xs(api, params)

        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
            "cookie": f"a1={a1}; web_session={web_session};",
            "origin": "https://www.xiaohongshu.com",
            "referer": "https://www.xiaohongshu.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "X-S": xs["X-s"],
            "X-S-Common": "",
            "X-T": str(xs["X-t"])
        }

        response = requests.post(url=url, headers=headers, data=json.dumps(params, separators=(",", ":")))
        time.sleep(random.uniform(0.2, 0.5))
        return response.text

    def parsel(self, item_dict):
        """
        解析
        :param item_dict:
        :return:
        """
        article_id = item_dict["article_id"]
        res = self.get_response(article_id)
        json_res = json.loads(res)

        note_card = json_res["data"]["items"][0]["note_card"]
        if "video" in note_card:
            video_url = note_card["video"]["media"]["stream"]["h264"][0]["backup_urls"][0].replace("'", "")
            item_dict.update({"type": "video", "url": video_url})
            self.down_loader(item_dict)

        for image in note_card["image_list"]:
            image_url = image["url"]
            item_dict.update({"type": "image", "url": image_url})
            self.down_loader(item_dict)

    def down_loader(self, item):
        """
        下载
        :param item:
        :return:
        """
        headers = {
            "referer": "https://www.xiaohongshu.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        }
        file_name = item["url"].split("/")[-1]
        dir_name = item['display_title'].replace(" ", "")
        if item["type"] == "image":
            image_content = requests.get(url=item["url"], headers=headers).content
            self.creade_dir(dir_name)
            with open(f"data/{dir_name}/{file_name}.jpg", mode="wb") as f:
                f.write(image_content)
                print(f"image: {file_name} complete")

        else:
            video_content = requests.get(url=item["url"], headers=headers).content
            self.creade_dir(dir_name)
            with open(f"data/{dir_name}/{file_name.split('.')[0]}.mp4", mode="wb") as f:
                f.write(video_content)
                print(f"video: {file_name} complete")

    def creade_dir(self, dir_name):
        """"""
        if not exists(join(self.download_path, dir_name)):
            mkdir(join(self.download_path, dir_name))

    def main(self, item_dict):
        """
        :param item_dict:
        :return:
        """
        self.parsel(item_dict)


# -------------------------------------------------
#                   首页spider
# -------------------------------------------------
def get_xs(api, data):
    """
    get xs
    :param api:
    :param data:
    :return:
    """
    with open("xs.js", mode="r", encoding="utf-8") as f:
        js_code = f.read()

    js_ = execjs.compile(js_code)
    xs = js_.call("get_xs", api, data, a1)
    return xs


def get_response_home(api, url="https://edith.xiaohongshu.com/api/sns/web/v1/homefeed"):
    """
    首页请求
    :param api:
    :param url:
    :return:
    """
    params = {
        "category": "homefeed.food_v3",
        "cursor_score": "1.6872598939340048E9",
        "note_index": 0,
        "num": 31,
        "refresh_type": 3,
        "search_key": "",
        "unread_begin_note_id": "",
        "unread_end_note_id": "",
        "unread_note_count": 0
    }
    xs = get_xs(api, params)
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "cookie": f"a1={a1}; web_session={web_session};",
        "origin": "https://www.xiaohongshu.com",
        "referer": "https://www.xiaohongshu.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "X-B3-Traceid": "9f2ddfd579b19e82",
        "X-S": xs["X-s"],
        "X-S-Common": "",
        "X-T": str(xs["X-t"])
    }

    response = requests.post(url=url, data=json.dumps(params, separators=(",", ":")), headers=headers).text
    return response


def parsel_res(res):
    """
    解析
    :param res:
    :return:
    """
    json_res = json.loads(res)
    item_list = json_res["data"]["items"]
    for item in item_list:
        article_id = item["id"]
        display_title = item["note_card"]["display_title"]

        pattern = r"[\u4e00-\u9fa5a-zA-Z0-9\s]+"  # 正则匹配，删除表情文件
        display_title = ", ".join(re.findall(pattern, display_title))
        item_dict = dict(zip(["article_id", "display_title"], [article_id, display_title]))
        print(item_dict)

        Downloader().main(item_dict)


def main():
    """
    :return:
    """
    api = "/api/sns/web/v1/homefeed"
    res = get_response_home(api)
    parsel_res(res)


if __name__ == '__main__':
    main()