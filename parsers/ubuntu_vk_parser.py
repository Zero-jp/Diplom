import csv
import requests

import vk_api


def take_posts(posts_count):
    token = '3613ed603613ed603613ed602936677349336133613ed60698bc05e0515374f6dce98c2'  # токен приложения, через которое программа получает данные
    version = 5.131  # версия вк
    owner_id = '-13922277'  # id группы
    count = 100  # получить 100 элементов
    offset = 0  # получить посты начиная с ...
    all_posts = []  # все полученные посты

    while offset < posts_count:
        response = requests.get('https://api.vk.com/method/wall.get',
                                params={
                                    'access_token': token,
                                    'v': version,
                                    'owner_id': owner_id,
                                    'count': count,
                                    'offset': offset
                                })
        data = response.json()['response']['items']
        offset += 100
        all_posts.extend(data)
    return all_posts


def file_writer(data):
    with open('ubuntu_posts.csv', 'w', encoding='utf-8') as file:
        pen = csv.writer(file)
        pen.writerow(('likes', 'body', 'id'))
        for post in data:
            pen.writerow((post['likes']['count'], post['text'], post['id']))


all_posts = take_posts(1000)
file_writer(all_posts)
