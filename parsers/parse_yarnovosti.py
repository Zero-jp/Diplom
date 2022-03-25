import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup, Tag
from parsers.news_site_parser import NewsSiteParser


class YarNovostiParser(NewsSiteParser):
    """
    Класс парсера разбирающего сайт https://yarnovosti.com/all/
    """

    @staticmethod
    def retrieve_further_news(request_data) -> list:
        """
        Получение последующих новостей с сайта для обработки

        Параметры:
        request_data - параметры для запроса на сервер, изменяются в процессе выполнения метода

        :return: список с новостями
        """
        website_url = 'https://yarnovosti.com/all/'
        headers_req = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0)\
            Gecko/20100101 Firefox/75.0', 'Accept': 'application/json, text/javascript, */*; q=0.01',
            'referer': 'https://yarnovosti.com/all/'
        }
        payload = {
            "action": "newsLiveLoad",
            "loaded": request_data['loaded'],
            "token": request_data['token'],
            "lastId": request_data['last_id'],
        }
        response_json = json.loads(requests.post(url=website_url, headers=headers_req, data=payload)
                                   .content.decode('utf-8-sig'))
        items = BeautifulSoup(response_json['html'], 'html.parser').find_all("article")
        request_data['last_id'] = items[-1].get("data-id")
        request_data['loaded'] += 18
        return items

    def parse_news_item(self, item: Tag) -> dict and bool:
        """
        Получение требуемой информации о новости.

        Параметры:
        item -- элемент типа Tag с данными об одной новости

        :return: именованный список с разобранной новостью, флаг(True, если текст новости пустой)
        """
        news_item = {}
        news_item['title'] = item.find("h3", class_="linkName").text
        news_item['link'] = item.find("h3", class_="linkName").find("a").get("href")
        news_item['full_text'] = ""
        news_item['categories'] = []
        for elem in item.find_all("p"):
            if self.tag_is_photo_caption(elem):
                news_item['full_text'] = news_item['full_text'] + elem.text + "\n"
        news_item['full_text'] = news_item['full_text'].strip()
        news_item['date_time'] = datetime.strptime(item.find("time").text, "%d.%m.%Y %H:%M")
        try:
            news_item['categories'] += [item.find("div", class_="categories").find("a").text]
        except AttributeError:
            news_item['categories'] = []
        news_item['source'] = "ЯрНовости"
        return news_item, False

    @staticmethod
    def tag_is_photo_caption(item: Tag) -> bool:
        """
        :return: True, если у тега нет класса
        """
        return item.get("class") is None

    def retrieve_first_news(self, earliest_date: datetime) -> dict and list and bool:
        """
        Получение полей для формирования запроса серверу сайта.
        Парсинг первой страницы списка новостей.

        Параметры:
        earliest_date -- дата начала периода, за который необходимо получать новости

        :return: список с данными для запроса на сервер; список, включающий в себя информациию о
        каждой новости, с первой страницы; флаг(True, если не достигнута последняя новость из заданного интервала)
        """
        request_data = {}
        html = super().retrieve_html('https://yarnovosti.com/all/')
        items = html.find("div", class_="news lenta").find_all("article")
        news, more_news_exists = super().parse_news_items(items, earliest_date)
        request_data['token'] = html.find("div", class_="news lenta").find("input").get("value")
        request_data['last_id'] = html.find("div", class_="news lenta").find_all("article")[-1].get("data-id")
        request_data['loaded'] = 18
        return request_data, news, more_news_exists
