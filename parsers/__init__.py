__all__ = ["news_site_parser", "parse_1yar", 'available_sources', 'parsers']

from parsers.parse_1yar import FirstYarParser
# from parsers.parse_76 import SeventySixParser
from parsers.parse_yarnews_net import YarnewsNetParser
from parsers.parse_yarnovosti import YarNovostiParser
# from parsers.parse_cnews import CnewsParser

available_sources = {"Первый Ярославский": '1yar', "76.ru": "76.ru", "YarNews": "yarnews", "ЯрНовости": "yarnovosti",
                     "Cnews": "cnews"}

parsers = {"1yar": FirstYarParser(),# "76.ru": SeventySixParser(), "cnews": CnewsParser(),
           "yarnews": YarnewsNetParser(), "yarnovosti": YarNovostiParser()}
