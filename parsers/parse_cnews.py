import re
import warnings
from datetime import datetime
import dateparser
import requests
from bs4 import BeautifulSoup
from parsers.news_site_parser import NewsSiteParser

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


class CnewsParser(NewsSiteParser):

    """
    Класс парсера, разбирающего сайт cnews.ru
    """

    def retrieve_article_date(self, link: str) -> any and bool:
        """
        Получение статьи и выделение из неё нужного текста.

        Параметры:
        link -- ссылка на новость

        :return: строка с текстом статьи
        """
        date = datetime
        event_article = bool
        article_html = super().retrieve_html(link)
        if 'events.cnews' in link:
            date = dateparser.parse(article_html.find('time', class_='form-hint').get_text()
                                    .replace('Мск', ''), date_formats=["%d.%m.%Y, %H:%M"],
                                    languages=['ru'])
            event_article = True
        if 'www.cnews' in link or 'safe.cnews' in link or 'mobile.cnews' in link \
                or 'innovations.cnews' in link:
            date = dateparser.parse(article_html.find('time', class_="article-date-mobile")
                                    .get_text(), date_formats=["%d %b %Y %H:%M"], languages=['ru'])
            event_article = False
        elif 'zoom.cnews' in link:
            date = dateparser.parse(article_html.find('div', class_="author", itemprop="datePublished")
                                    .get_text(), date_formats=["%d %B %Y"], languages=['ru'])
            event_article = False
        elif 'storage.cnews' in link:
            date = dateparser.parse(article_html.find('div', class_="article_data").find('time')
                                    .get_text(strip=True), date_formats=["%d %B %Y"],
                                    languages=['ru'])
            event_article = False
        return date, event_article

    def retrieve_article_text(self, link: str) -> str:
        """
        Получение статьи и выделение из неё нужного текста.

        Параметры:
        link -- ссылка на новость

        :return: строка с текстом статьи
        """
        full_text = ''
        text_parts = []
        if 'www.cnews' in link or 'safe.cnews' in link:
            text_parts = super().retrieve_html(link).find('article', class_="news_container").find_all('p')
        elif 'zoom.cnews' in link:
            text_parts = super().retrieve_html(link).find('div', class_="article_text NewsBody").find_all('p')
        for part in text_parts:
            full_text = full_text + part.get_text().strip() + '\n'
        return full_text

    def retrieve_correct_link(self, news_item: dict) -> str and bool:
        if news_item['title'].startswith('ZOOM.CNews:'):
            return 'https://zoom.cnews.ru' + news_item['link'], False
        return 'crash', True

    def parse_news_item(self, item: any) -> dict and bool:
        """
        Получение требуемой информации о новости.

        Параметры:
        item -- элемент типа Tag с данными об одной новости

        :return: именованный список с разобранной новостью, флаг (True, если текст новости пустой)
        """
        news_item = {}
        news_item['title'] = item.find('a').get_text()
        news_item['link'] = item.find('a').get('href')
        news_unreachable = False
        if news_item['link'].split('/')[0] != 'https:':
            news_item['link'], news_unreachable = self.retrieve_correct_link(news_item)
        if news_unreachable: return news_item, True
        news_item['date_time'], retrieve_event_article = self.retrieve_article_date(news_item['link'])
        if retrieve_event_article:
            return news_item, True
        news_item['full_text'] = self.retrieve_article_text(news_item['link'])
        try:
            news_item['categories'] = [super().retrieve_html(news_item['link']).find('a', class_="header-client-logo")
                                           .get_text()]
        except AttributeError:
            news_item['categories'] = list()
        news_item['source'] = 'Cnews'
        news_item['authors_name'] = news_item['authors_rate'] = news_item['authors_rate_score'] = \
            news_item['likes_count'] = news_item['dislikes_count'] = news_item['comments'] = news_item['reposts'] = ''
        return news_item, False

    def retrieve_first_news(self, earliest_date: datetime) -> dict and list and bool:
        """
        Формирование параметров request_data для запросов на сервер

        Параметры:
        earliest_date -- дата начала периода, за который необходимо получать новости

        :return: список с данными для запроса на сервер; список для новостей;
        флаг(True, если не достигнута последняя новость из заданного интервала)
        """
        html = super().retrieve_html('https://www.cnews.ru/news')
        items = html.find('div', class_="allnews_mainpage").find_all(class_=re.compile("allnews_item"))
        news, more_news_exists = super().parse_news_items(items, earliest_date)
        request_data = {'website_url': 'https://www.cnews.ru/news',
                        'more_news_url': 'https://www.cnews.ru' + html.find('a', id="allnews_more").get('href')}
        return request_data, news, more_news_exists

    def retrieve_further_news(self, request_data: str) -> list:
        """
        Получение последующих новостей с сайта для обработки

        Параметры:
        request_data - параметры для запроса на сервер, изменяются в процессе выполнения метода

        :return: список с новостями
        """
        headers_req = {
            'Host': 'www.cnews.ru',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'referer': request_data['website_url']
        }
        request_data['headers_req'] = headers_req
        request = requests.get(url=request_data['more_news_url'], headers=request_data['headers_req'])
        loaded_news = BeautifulSoup(request.text, 'html.parser').find_all('div', class_="allnews_item")
        request_data['more_news_url'] = 'https://www.cnews.ru' + BeautifulSoup(request.text, 'html.parser') \
            .find('a', class_="read_more_btn").get('href')
        return loaded_news
