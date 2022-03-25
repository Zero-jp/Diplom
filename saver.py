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
        # Считывать имя скриптов, из которых получается информация?
        # if data['parser_name'] == 'vk_parser':
        #     with open('texts.csv', 'w') as file:
        #         storage = csv.writer(file)
        #         storage.writerow(('likes', 'body', 'id'))
        #         # Можно записывать сразу список? (ускорит прогу)
        #         for item in data['items']:
        #             storage.writerow((item['likes']['count'], item['text'], item['id']))
        # else:
        with open('texts.csv', 'w') as file:
            storage = csv.writer(file)
            storage.writerow(('title', 'link', 'full_text', 'categories', 'date_time', 'source'))
            for items in data:
                for item in items:
                    storage.writerow((item['title'], item['link'], item['full_text'],
                                      item['categories'], item['date_time'], item['source']))
