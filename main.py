from pprint import pprint as pp
import requests as rq
import bs4
from fake_headers import Headers
import os
import re
import json


# если нужна выдача строго по заданию, то оставить тоолько django и flask
# с вероятность 99.9(9)% параметр '?text=python'
# при этом будет "как бы" учтён,
# но будет не 'django' & 'flask', а 'django' | 'flask'

# просто сначала написал код, только потом перечитал задание
# переписать код для отбора сначала по python,
# а потом по 'django' & 'flask' - это тоже время и гвозди.
# надеюсь, уже написанного будет достаточно, чтобы подтвердить,
# что суть я уловил, если нет, ну что ж... перепишу...
KEYWORDS = ['django', 'flask', 'python', 'oracle']
SEARCH_HREF = 'https://hh.ru/search/vacancy'
USD_FAN = False
FILENAME = 'vacancies.json'
DELETE_JSONFILE_AFTER_PPRINT = True


def get_href_by_kw(p_key_word: str):
    if p_key_word is None or p_key_word == '':
        return SEARCH_HREF + '?area=1&area=2'
    return SEARCH_HREF + '?text=' + p_key_word + '&area=1&area=2'


def is_text_match(p_text: str):
    for word in KEYWORDS:
        if re.search(r'\b' + word + r'\b', p_text, flags=re.I) is not None:
            return word


def get_search_html(p_key_word: str):
    headers = Headers(browser='firefox', os='win')
    headers_data = headers.generate()
    search_page_html = rq.get(get_href_by_kw(p_key_word),
                              headers=headers_data
                              ).text
    search_page_html = bs4.BeautifulSoup(search_page_html, 'lxml')
    return search_page_html


def get_match_vacansies_lst(p_search_page_html):
    div_search_tags = p_search_page_html.find_all('div',
                                                  class_='serp-item')
    return div_search_tags


if __name__ == '__main__':

    div_article_list_tags = list()
    for word in KEYWORDS:
        search_page_html = get_search_html(word)
        div_search_tags = get_match_vacansies_lst(search_page_html)
        div_article_list_tags += div_search_tags

    lst = list()
    for div in div_article_list_tags:
        vacancy_name = div.find(attrs={'class': 'serp-item__title',
                                       'data-qa': 'serp-item__title'
                                       }
                                ).get_text('data-qa')
        employer = div.find(attrs={'class': 'bloko-link bloko-link_kind'
                                            '-tertiary',
                                   'data-qa': 'vacancy-serp__vacancy'
                                              '-employer'
                                   }
                            ).get_text('data-qa')
        employer = employer.replace('\xa0data-qa', ' ')

        href = div.find(class_='bloko-link').get('href')
        href = href if href.startswith('https://adsrv.')\
            else href[0: href.find('?')]

        fork = str()
        city = str()
        if div.find(class_='bloko-header-section-2') is not None:
            fork = div.find(class_='bloko-header-section-2'
                            ).get_text('data-qa')
            fork = fork.replace('data-qa', '')
            fork = fork.replace(u'\u202f', ' ')
        if div.find(attrs={'class': 'bloko-text',
                           'data-qa': 'vacancy-serp__vacancy-address'
                           }
                    ) is not None:
            city = div.find(attrs={'class': 'bloko-text',
                                   'data-qa': 'vacancy-serp__vacancy-address'}
                            ).get_text('data-qa')
            city = re.search('[а-я-]+', city, flags=re.I).group()

            if not USD_FAN:
                lst.append((vacancy_name, employer, href, fork, city))
            elif fork.endswith('$'):
                lst.append((vacancy_name, employer, href, fork, city))

    try:
        os.remove(FILENAME)
    except FileNotFoundError:
        pass

    lst_len = len(lst)
    with open(FILENAME, 'a', encoding='UTF-8') as file:
        file.write('{"vacancies": [')
        for i, elmt in enumerate(lst, start=1):
            dct = {'vacancy_name': elmt[0],
                   'employer': elmt[1],
                   'href': elmt[2],
                   'fork': elmt[3],
                   'city': elmt[4]
                   }
            file.write(json.dumps(dct, ensure_ascii=False)
                       + (',' if i < lst_len else '')
                       )
        file.write(']}')
    with open(FILENAME, 'r', encoding='UTF-8') as file:
        result = json.loads(file.read())
        # pprint не умеет красиво выводить JSON, так что в виде словаря
        pp(result)
        # pp(json.dumps(result, ensure_ascii=False))

    if DELETE_JSONFILE_AFTER_PPRINT:
        os.remove(FILENAME)
