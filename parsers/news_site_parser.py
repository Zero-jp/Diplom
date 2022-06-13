""" This class describes abstract class for news site parser """
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from bs4 import BeautifulSoup
import requests


headers_req = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0)\
     Gecko/20100101 Firefox/75.0', 'accept': '*/*'
}

class SiteUnreachableException(Exception):
    """ Исключение, описывающее ситуацию, при которой не удаётся подключиться к новостному сайту"""


class NewsSiteParser(ABC):
    """ News site parsers gets information from news sites """

    @abstractmethod
    def retrieve_first_news(self, earliest_date: datetime):
        """
        Получение полей для формирования запроса серверу сайта.
        Парсинг первой страницы списка новостей.

        Параметры:
        earliest_date -- дата начала периода, за который необходимо получать новости

        :return: список с данными для запроса на сервер; список, включающий в себя информациию о
        каждой новости, с первой страницы; флаг(True, если не достигнута последняя новость из заданного интервала)
        """

    @abstractmethod
    def retrieve_further_news(self, request_data: dict):
        """
        Получение последующих новостей с сайта для обработки.

        Параметры:
        request_data - параметры для запроса на сервер, изменяются в процессе выполнения метода

        :return: список с новостями
        """

    def parse(self, earliest_date: datetime) -> list:
        """
        Обработка данных новостей взятых с сайта.

        Параметры:
        earliest_date -- дата начала периода, за который необходимо получать новости

        :return: список, включающий в себя информациию о каждой новости
        """
        request_data, news, more_news_exists = self.retrieve_first_news(earliest_date)
        while more_news_exists:
            download_items = self.retrieve_further_news(request_data)
            download_news, more_news_exists = self.parse_news_items(download_items, earliest_date)
            news += download_news
        return news

    def parse_news_items(self, items: list, earliest_date: datetime) -> list and bool:
        """
        Получение требуемой информации о новостях из html кода списка новостей с сайта.

        Параметры:
        items -- список элементов типа Tag с данными о каждой новости
        earliest_date -- дата начала периода, за который необходимо получать новости

        :return: список из словарей с разобранными новостями, флаг (True, если не достигнута последняя новость
                                                                                        из заданного интервала)
        """
        news = []
        for item in items:
            news_item, text_empty = self.parse_news_item(item)
            if not text_empty and news_item['date_time'] > earliest_date:
                news.append(news_item)
                NewsSiteParser.log_article_parsed(news_item)
            elif text_empty:
                continue
            else:
                return news, False
        return news, True

    @abstractmethod
    def parse_news_item(self, item) -> dict and bool:
        """
        Получение требуемой информации о новости.

        Параметры:
        item -- элемент типа Tag с данными об одной новости

        :return: именованный список с разобранной новостью, флаг (True, если текст новости пустой)
        """

    @staticmethod
    def retrieve_html(website_url):
        """
        Getting html-code of the web-site
        :return: html code
        """

        try:
            website_response = requests.get(website_url, headers=headers_req)
        except requests.exceptions.Timeout:
            print("Timeout occurred")
        if website_response.status_code != requests.codes.ok:
            raise SiteUnreachableException()
        return BeautifulSoup(website_response.content, 'html.parser')

    @staticmethod
    def log_article_parsed(article: dict):
        """ Prints the article publication date and the article title to the stderr """
        print(f' {article["date_time"].strftime("%Y-%m-%d %H:%M:%S")}\t{article["title"]}', file=sys.stderr)
