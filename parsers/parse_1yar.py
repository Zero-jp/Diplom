import json
from datetime import datetime
import nums_from_string
import requests
from bs4 import BeautifulSoup

from parsers.news_site_parser import NewsSiteParser


class FirstYarParser(NewsSiteParser):
    """
    Класс парсера разбирающего сайт https://1yar.tv/all/
    """

    @staticmethod
    def retrieve_further_news(request_data) -> list:
        """
        Получение последующих новостей с сайта.

        Параметры:
        request_data - параметры для запроса на сервер, изменяются в процессе выполнения метода

        :return: список с новостями
        """
        website_url = 'https://1yar.tv/'
        headers_req = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0)\
             Gecko/20100101 Firefox/75.0', 'Accept': 'application/json, text/javascript, */*; q=0.01',
            'referer': 'https://1yar.tv/all/'
        }
        payload = {
            "action": "newsLiveLoad",
            "loaded": request_data['len_news'],
            "token": request_data['token'],
            "lastId": request_data['last_id'],
            "_": ""
        }
        request = json.loads(
            requests.post(url=website_url, headers=headers_req, data=payload).content.decode('utf-8-sig'))
        loaded_news = BeautifulSoup(request['html'], 'html.parser').find_all('article')
        request_data['last_id'] = loaded_news[-1].get('data-id')
        return loaded_news

    def parse_news_item(self, item: any) -> dict and bool:
        """
        Получение требуемой информации о новости.

        Параметры:
        item -- элемент типа Tag с данными об одной новости

        :return: именованный список с разобранной новостью, флаг (True, если текст новости пустой)
        """
        news_item = {}
        news_item['title'] = item.find('h3', class_='linkName').get_text()
        news_item['link'] = item.find('h3', class_='linkName').find('a').get('href')
        article_body_tag = super().retrieve_html((item.find('a', itemprop='url').get('href'))) \
            .find('span', itemprop='articleBody')
        news_item['full_text'] = ""
        article_is_ad = False
        if not article_body_tag:
            return {}, True
        for p_tag in article_body_tag.find_all(name='p'):
            if self.tag_is_photo_caption(p_tag):
                continue
            if self.tag_is_ad_reference(p_tag):
                article_is_ad = True
                continue
            news_item['full_text'] += p_tag.get_text().strip() + "\n"
        news_item['full_text'] = news_item['full_text'].strip()
        news_item['date_time'] = datetime.strptime(item.find('time', itemprop='datePublished').get('content'),
                                                   "%Y-%m-%dT%H:%M:%S")
        if news_item['full_text'] == '': return news_item, True
        try:
            news_item['categories'] = [item.find('div', class_='categories').get_text(strip=True)]
        except AttributeError:
            news_item['categories'] = list()
        if article_is_ad:
            news_item['categories'].append('Реклама')
        meta_author = super().retrieve_html((item.find('a', itemprop='url').get('href'))).find('div', id='author_news')
        if meta_author.find('div', class_='author').find('a'):
            news_item['authors_name'] = meta_author.find('div', class_='author').find('a').get_text(strip=True)
            try:
                news_item['authors_rate'] = nums_from_string.to_num(meta_author.find('div', class_='author').find('div', class_='rating')\
                    .find('div', class_='current').get('data-value'))
            except ValueError:
                news_item['authors_rate'] = ''
            news_item['authors_rate_score'] = nums_from_string.get_nums(meta_author.find('div', class_='author').find('div', class_='rating')\
                .get_text(strip=True))[0]
        else: news_item['authors_name'] = news_item['authors_rate'] = news_item['authors_rate_score'] = ''
        news_item['likes_count'] = nums_from_string.get_nums(meta_author.find('div', class_='rate').find('a', class_='icons-like')\
            .get_text(strip=True))[0]
        news_item['dislikes_count'] = nums_from_string.get_nums(meta_author.find('div', class_='rate').find('a', class_='icons-dislike')\
            .get_text(strip=True))[0]
        news_item['source'] = 'Первый Ярославский'
        news_item['comments'] = news_item['reposts'] = ''
        return news_item, False

    @staticmethod
    def tag_is_photo_caption(tag: BeautifulSoup) -> bool:
        """
        :return: True if the tag contains an <em> tag that means the <em> tag is a photo caption, otherwise False
        """
        return tag.find('em') is not None

    @staticmethod
    def tag_is_ad_reference(tag: BeautifulSoup) -> bool:
        """
        :return: True if the tag contains an <a> tag with href attribute refers to https://1yar.tv/article/p/
        that means the article is ad, otherwise False
        """
        return tag.find(name='a', attrs={'href': 'https://1yar.tv/article/p/'}) is not None

    def retrieve_first_news(self, earliest_date: datetime) -> dict and list and bool:
        """
        Получение полей для формирования запроса серверу сайта.
        Парсинг первой страницы списка новостей.

        Параметры:
        earliest_date -- дата начала периода, за который необходимо получать новости

        :return: список с данными для запроса на сервер; список, включающий в себя информациию о
        каждой новости, с первой страницы; флаг (True, если не достигнута последняя новость из заданного интервала)
        """
        request_data = {}
        html = super().retrieve_html('https://1yar.tv/vse/')
        items = html.find('div', class_='news').find_all('article')
        news, more_news_exists = super().parse_news_items(items, earliest_date)
        request_data['token'] = html.find('div', id='center').find('input').get('value')
        request_data['last_id'] = html.find('div', class_='news').find('article', attrs={"data-id": True}).get(
            'data-id')
        request_data['len_news'] = len(news)
        return request_data, news, more_news_exists
