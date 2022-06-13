# from src.parsers.parser_cyc import run_parse - поставлена проверка на бота

from datetime import datetime
import sys
import json
from bson import json_util

from parsers import parsers
import saver


def run_parser(parser_name, from_date: datetime):
    """ Finds and runs a parser with specified name. """
    return parsers[parser_name].parse(from_date)


if __name__ == '__main__':
    date = datetime.fromisoformat(sys.argv[1])
    texts = []
    for parser in parsers:
        texts.append(run_parser(parser, date))
        # break
    # print(json.dumps(texts, default=json_util.default, ensure_ascii=False), end='\n\n')
    saver.Saver.file_writer(texts)
