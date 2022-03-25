import re
from abc import ABC
from bs4 import BeautifulSoup
import requests

url = "https://www.cyberforum.ru/"
headers_req = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0)\
     Gecko/20100101 Firefox/75.0', 'accept': '*/*'
}


def request_page(website_url, headers=None) -> requests.Response:
    """
    Executes a http GET request to the url.
    :return: Response object.
    """
    if not headers:
        headers = headers_req
    website_response = requests.get(website_url, headers=headers)
    if website_response.status_code != requests.codes.ok:
        raise SiteUnreachableException()
    return website_response


def retrieve_html(website_url):
    """
    Getting html-code of the web-site
    :return: html code
    """
    website_response = request_page(website_url, headers=headers_req)
    return BeautifulSoup(website_response.content, 'html.parser')


def retrieve_articles_html(website_url):
    main_page_html = retrieve_html(website_url)
    print(main_page_html)


def retrieve_articles_html(website_url):
    main_page_html = retrieve_html(website_url)
    print(main_page_html)


# def log_article_parsed(article: dict):
#     """ Prints the article publication date and the article title to the stderr """
#     print(f' {article["date_time"].strftime("%Y-%m-%d %H:%M:%S")}\t{article["title"]}', file=sys.stderr)


class SiteUnreachableException(Exception):
    """ Исключение, описывающее ситуацию, при которой не удаётся подключиться к новостному сайту"""


def forum_retrive(item):
    out = {}
    out['header'] = item.find('h1').getText()
    out['date'] = item.find('div', class_='smallfont shade').getText()[0:17]
    out['rate'] = item.find('td', id='threadrating').find('span', title='Средняя оценка').getText()
    out['mark_count'] = item.find('td', id='threadrating').find('span', title='Всего голосов').getText()
    out['category'] = item.find_all('div', class_='smallfont shade')[1].getText()[6:-13]
    out['messages'] = message_retrive(item)
    return out


def message_retrive(item):
    out = []
    messages_html = item.find_all('div', attrs={'id': re.compile("post_message_")})
    for message_html in messages_html:
        out.append(message_html.getText().replace(u'\xa0', u' '))
    return out


def write_down(results: list):
    f = open('masseges', 'w')
    f.write('Название форума: ' + results['header'] + '.\n')
    f.write('Дата создания форума: ' + results['date'] + '.\n')
    f.write('Рейтинг: ' + results['rate'] + '. Колличество оценок: ' + results['mark_count'] + '.\n')
    f.write('Категории: ' + results['category'] + '.\n')
    f.write('Сообщения: ' + '\n')
    for mess in results['messages']:
        f.write(mess + '\n')
    f.close()


"""html = retrieve_html(url)
items = html.find_all('td', class_="alt1Active")
chapter_href = []
for item in items:
    chapter_href.append(item.find('a').get('href'))
subchapter_href = []
for cl_href in chapter_href:
    temp_url = retrieve_html(cl_href)
    try:
        max_page = temp_url.find('div', class_='pagenav').find('td', class_='vbmenu_control').getText().split()[-1]
    except:
        max_page = '1'
    page = 1
    while page <= int(max_page):
        temp_url[-1] = '-page' + str(page) + '.html'
        subchapter_href.append(
            temp_url.find('table', id='threadslist').find_all('tr', attrs={'id': re.compile("vbpostrow")}))
        page += 1
article_href = []
for sub_href in subchapter_href:
    for sub in sub_href:
        article_href.append(sub.find('a').get('href'))
messeges = []
for article in article_href:
    messeges.append(retrieve_html(article).find_all('div', attrs={'id': re.compile("post_message_")}))
output = []
c = 0
while c < 2:
    for messege in messeges:
        for mes in messege:
            output.append(messege.getText())
        c += 1
print(output)
print(len(output))"""

def run_parse():
    out_put = forum_retrive(retrieve_html('https://www.cyberforum.ru/cpp-beginners/thread1391513.html'))
    write_down(out_put)
    print(out_put)
