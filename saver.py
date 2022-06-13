import csv


class Saver():
    """
    Класс записывающий в текстовый документ
    """

    def file_writer(data: list):
        """
        Сохранение полученых данных.

        Параметры:
        data -- асооциативный список с текстами и метаданными

        :return:
        """
        with open('texts.csv', 'w', encoding='utf-8') as file:
            storage = csv.writer(file)
            storage.writerow(('title', 'link', 'full_text', 'categories', 'date_time', 'source', 'authors_name',
                              'authors_rate', 'authors_rate_score', 'likes_count', 'dislikes_count', 'comments',
                              'reposts'))
            for items in data:
                for item in items:
                    storage.writerow((item['title'], item['link'], item['full_text'],
                                      item['categories'], item['date_time'], item['source'],
                                      item['authors_name'], item['authors_rate'], item['authors_rate_score'],
                                      item['likes_count'], item['dislikes_count'], item['comments'], item['reposts']))
        file.close()
