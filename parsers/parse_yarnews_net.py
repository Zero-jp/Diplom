import re
from datetime import datetime

from parsers.news_site_parser import NewsSiteParser


class YarnewsNetParser(NewsSiteParser):
    """
    Класс парсера разбирающего сайт https://www.yarnews.net/
    """

    def retrieve_article_text(self, link: str) -> str:
        """
        Получение статьи и выделение из неё нужного текста.

        Параметры:
        link -- ссылка на новость

        :return: строка с текстом статьи
        """
        full_text = ''
        text_parts = super().retrieve_html(link).find('div', class_="text").find_all('p')
        for part in text_parts:
            part = part.get_text()
            strong_tag = str(re.search(r'<.strong>', part))
            full_text = full_text + part.replace(strong_tag, ' ').strip() + '\n'
        return full_text

    def parse_news_item(self, item: any) -> dict and bool:
        """
        Получение требуемой информации о новости.

        Параметры:
        item -- элемент типа Tag с данными об одной новости

        :return: именованный список с разобранной новостью, флаг (True, если текст новости пустой)
        """
        news_item = {}
        news_item['title'] = item.find('a', class_='news-name').get_text()
        news_item['link'] = "https://www.yarnews.net" + item.find('a', class_='news-name').get('href')
        news_item['full_text'] = self.retrieve_article_text(news_item['link'])
        news_item['date_time'] = datetime.strptime(item.find('span', class_="news-date").get_text(),
                                                   "%d.%m.%Y в %H:%M")
        news_item['categories'] = list()
        news_item['source'] = 'YarNews'
        return news_item, False

    @staticmethod
    def retrieve_first_news(earliest_date: datetime) -> dict and list and bool:
        """
        Формирование параметров request_data для запросов на сервер

        Параметры:
        earliest_date -- дата начала периода, за который необходимо получать новости

        :return: список с данными для запроса на сервер; список для новостей;
        флаг(True, если не достигнута последняя новость из заданного интервала)
        """
        return {"news_loaded": 0}, [], True

    def retrieve_further_news(self, request_data) -> list:
        """
        Получение последующих новостей с сайта для обработки

        Параметры:
        request_data - параметры для запроса на сервер, изменяются в процессе выполнения метода

        :return: список с новостями
        """
        request = super().retrieve_html('https://www.yarnews.net/news/chronicle/ajax/'
                                        + str(request_data['news_loaded']) + '/')
        items = request.find_all('div', class_="news-feed-info")
        request_data['news_loaded'] += 30
        return items
