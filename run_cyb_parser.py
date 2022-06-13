from datetime import datetime
import sys
import json
from bson import json_util

from parsers import parser_cy
import saver


def run_parser(url: str):
    """ Finds and runs a parser with specified name. """
    return parser_cy["cyb"].parse(url)


if __name__ == '__main__':
    texts = run_parser('https://www.cyberforum.ru')
        # break
    # print(json.dumps(texts, default=json_util.default, ensure_ascii=False), end='\n\n')
    saver.Saver.forum_writer(texts)