from datetime import datetime

from parsers.news_site_parser import NewsSiteParser


def tag_deduplicate(double_tag: str, text: any, changing: str):
    """
    Замена двух дублирующихся символов на один.

    Параметры:
    double_tag -- символ, который нужно заменить
    changing -- символ, на который заменяются дублированные символы в html
    """
    for tag in text.find_all(double_tag):
        if tag.next_element == tag:
            tag.next_element.replace_with(changing)
            tag.replace_with('')


class SeventySixParser(NewsSiteParser):
    """
    Класс парсера разбирающего сайт https://76.ru/text/
    """

    def retrieve_article_comments(self, comments_html) -> str:
        out = []
        comments_html.find('section', id="comments-wrap").find('div').decompose()
        comments = comments_html.find('section', id="comments-wrap").findAll('div', attrs={"id": True})
        for comment in comments:
            data = {'author_name': str(comment.find('div', itemprop="creator").get_text()),
                    'comment': str(comment.find('p', itemprop="commentText").get_text())}
            out.append(data['author_name'] + ": " + data['comment'])
        return out

    def retrieve_article_text(self, article_html) -> str:
        """
        Получение статьи и выделение из неё нужного текста.

        Параметры:
        link -- ссылка на новость

        :return: строка с текстом статьи
        """
        full_text = ''
        article_body_tag = article_html.find('div', itemprop="articleBody")
        if article_body_tag:
            article_body_tag.find('div', id="record-header").decompose()
            body = article_body_tag.findChild()
            body_parts = body.findChildren()
            try:
                article_body_tag.find('figure').decompose()
            except:
                pass
            text_parts = article_body_tag.find('div').find_all('div', recursive=False)
        else:
            return full_text
        for part in text_parts:
            try:
                if part.find('div').find('p').get_text() == "Поделиться": continue
                tag_deduplicate('br', part, '\n')
                for text in part.find('div').find_all(['p', 'li'], []):
                    full_text = full_text + text.get_text() + '\n'
            except AttributeError:
                pass
        return full_text.strip()

    def parse_news_item(self, item: any) -> dict and bool:
        """
        Получение требуемой информации о новости.

        Параметры:
        item -- элемент типа Tag с данными об одной новости

        :return: именованный список с разобранной новостью, флаг (True, если текст новости пустой)
        """
        news_item = {}
        news_item['title'] = item.find('h2').find('a').get_text()
        news_item['link'] = item.find('a').get('href')
        if news_item['link'].split('/')[4] == 'longread':
            return news_item, True
        if news_item['link'].find("http") == -1: news_item['link'] = "https://76.ru" + news_item['link']
        news_item['date_time'] = datetime.strptime(item.find('time').get('datetime'), "%Y-%m-%dT%H:%M:%S")
        article_html = super().retrieve_html(news_item['link'])
        try:
            news_item['authors_name'] = article_html.find('div', itemprop="author").find('p', itemprop="name")\
                .get_text(strip=True)
            news_item['author_position'] = article_html.find('div', itemprop="author").find('p', itemprop="position")\
                .get_text(strip=True)
        except:
            news_item['authors_name'] = ''
            news_item['author_position'] = ''
        categories = article_html.find('div', id='record-header').find('div').find('div').findAll('span')
        news_item['categories'] = []
        for category in categories:
            news_item['categories'].append(category.getText())
        news_item['comments'] = []
        try:
            if article_html.find('div', class_="mobile tablet laptop desktop").find('span').getText() != '(0)':
                news_item['comments'] = self.retrieve_article_comments(super().retrieve_html(news_item['link'] +
                                                                                             'comments/'))
        except AttributeError:
            pass
        news_item['full_text'] = self.retrieve_article_text(article_html)
        if news_item['full_text'] == '': return news_item, True
        news_item['source'] = '76.ru'
        news_item['authors_rate'] = news_item['authors_rate_score'] = news_item['likes_count'] =\
            news_item['dislikes_count'] = news_item['reposts'] = ''
        return news_item, False

    @staticmethod
    def retrieve_first_news(earliest_date: datetime) -> dict and list and bool:
        """
        Формирование параметров request_data для запросов на сервер.

        Параметры:
        earliest_date -- дата начала периода, за который необходимо получать новости

        :return: список с данными для запроса на сервер; список для новостей;
        флаг(True, если не достигнута последняя новость из заданного интервала)
        """
        return {"page": 1}, [], True

    def retrieve_further_news(self, request_data) -> list:
        """
        Получение последующих новостей с сайта для обработки

        Параметры:
        request_data - параметры для запроса на сервер, изменяются в процессе выполнения метода

        :return: список с новостями
        """
        # print('https://76.ru/text/?page=' + str(request_data['page']))
        news_html = super().retrieve_html('https://76.ru/text/?page=' + str(request_data['page']))
        items = news_html.find('div', class_='central-column-container').find_all('article')
        request_data['page'] += 1
        return items
