__all__ = ["news_site_parser", "parse_1yar", 'available_sources', 'parsers']

from parsers.parse_1yar import FirstYarParser
from parsers.parse_76 import SeventySixParser
from parsers.parse_yarnews_net import YarNewsNetParser
from parsers.parse_yarnovosti import YarNovostiParser
from parsers.parse_cnews import CnewsParser

from parsers.ubuntu_vk_parser import VkParse

available_sources = {"Первый Ярославский": '1yar', "YarNews": "yarnews", "76.ru": "76.ru", "ЯрНовости": "yarnovosti",
                     "Cnews": "cnews", "cyberforum": "cyb", "Новостная группа в ВК Ubuntu": "VkUnuntu"}

parsers = {"1yar": FirstYarParser(), "76.ru": SeventySixParser(), "cnews": CnewsParser(),
           "yarnews": YarNewsNetParser(), "yarnovosti": YarNovostiParser(), "VkUbuntu": VkParse()}

