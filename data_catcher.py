"""
Скрипт для получения/обновления текстов и мета-данных.
"""

from saver import Saver
from run_parsers import run_parser

data = run_parser()
Saver.file_writer(data)
