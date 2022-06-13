import csv
from datetime import datetime

import requests
from parsers.news_site_parser import NewsSiteParser

import vk_api

offset = 0

request_data = {
    # токен приложения, через которое программа получает данные
    "token": '3613ed603613ed603613ed602936677349336133613ed60698bc05e0515374f6dce98c2',
    # версия вк
    "version": 5.131,
    # id группы
    "owner_id": '-13922277',
    # получать по 100 элементов
    "count": 100,
    # получить посты начиная с ...
    "offset": offset
}


class VkParse(NewsSiteParser):
    """
    Парсер группы в вк https://vk.com/club13922277
    """

    def retrieve_first_news(self, earliest_date: datetime) -> dict and list and bool:
        """
        Формирование параметров request_data для запросов на сервер

        Параметры:
        earliest_date -- дата начала периода, за который необходимо получать новости

        :return: список с данными для запроса на сервер; список для новостей;
        флаг(True, если не достигнута последняя новость из заданного интервала)
        """
        return request_data, [], True

    def retrieve_further_news(self, request_data):
        global offset
        response = requests.get('https://api.vk.com/method/wall.get',
                                params={
                                    'access_token': request_data["token"],
                                    'v': request_data["version"],
                                    'owner_id': request_data["owner_id"],
                                    'count': request_data["count"],
                                    'offset': request_data["offset"]
                                })
        download_items = response.json()['response']['items']
        offset += 100
        return download_items

    def parse_news_item(self, item):
        news_item = {}
        news_item['date_time'] = datetime.fromtimestamp(item["date"])
        news_item['link'] = "https://vk.com/ubuntu_ru?w=wall-13922277_" + str(item["id"]) + "%2Fall"
        news_item['title'] = "Ссылка на пост: " + news_item['link'] + " "
        if item["marked_as_ads"] != 0 or item["text"] == "":
            return news_item, True
        news_item['full_text'] = item["text"]
        news_item['likes_count'] = item["likes"]["count"]
        news_item['comments'] = self.retrive_comments(item)
        news_item['reposts'] = item['reposts']["count"]
        news_item['categories'] = news_item['source'] = news_item['authors_name'] = news_item['authors_rate'] \
            = news_item['authors_rate_score'] = news_item['dislikes_count'] = ''
        return news_item, False

    def retrive_comments(self, post):
        comments = []
        response = requests.get('https://api.vk.com/method/wall.getComments',
                                params={
                                    'access_token': request_data['token'],
                                    'v': request_data['version'],
                                    'owner_id': post["owner_id"],
                                    'post_id': post["id"],
                                    'need_likes': 1,
                                    'extended': 1,
                                    'offset': 0
                                })
        if 'response' not in response.json(): return comments
        download_items = response.json()['response']['items']
        download_profiles = response.json()['response']['profiles']
        for download_item in download_items:
            if download_item["text"] == '': continue
            comments.append(self.retrive_comment(download_item, download_profiles))
        return comments

    def retrive_comment(self, comment, profiles):
        comment_item = {}
        comment_item['date_time'] = datetime.fromtimestamp(comment["date"]).strftime('%Y-%m-%d %H:%M:%S')
        comment_item['full_text'] = comment["text"]
        comment_item['likes_count'] = comment["likes"]["count"]
        for profile in profiles:
            if comment['from_id'] == profile['id']:
                comment_item['author_name'] = profile["first_name"] + " " + profile["last_name"]
        return comment_item
