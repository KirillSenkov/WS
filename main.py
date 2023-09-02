from pprint import pprint as pp
from datetime import datetime as dt
t = dt.now()
t = t.strftime('%m/%d/%Y %H:%M:%S')

import requests as rq
import bs4
from fake_headers import Headers
import re
from pprint import pprint as pp


SEARCH_HREF = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
KEYWORDS = ['django', 'flask', 'python']
#USD_FAN = True



def is_text_match(p_text: str):
    for word in KEYWORDS:
        if re.search(r'\b' + word + r'\b', p_text, flags=re.I) is not None:
            return word


def get_search_html():
    headers = Headers(browser='firefox', os='win')
    headers_data = headers.generate()
    search_page_html =\
        rq.get(SEARCH_HREF,
               headers=headers_data
               ).text
    search_page_html = bs4.BeautifulSoup(search_page_html, 'lxml')
    return search_page_html


def get_match_vacansies_lst(p_search_page_html):
    div_search_tags = p_search_page_html.find_all('div',
                                                  class_='serp-item')
    return div_search_tags


if __name__ == '__main__':

    search_page_html = get_search_html()

    div_search_tags = get_match_vacansies_lst(search_page_html)

    div_article_list_tags = div_search_tags

    for div in div_article_list_tags:
        if is_text_match(div.text) and div.text.find('дисциплин') > 0:
            href = div.find(class_='serp-item__title').get('href')
            fork = div.find(attrs={'data-qa': True}
                            ).get('data-qavacancy-serp__vacancy-compensation')
            pp(div)
    # Записать в json информацию о каждой вакансии:
    # - ссылка
    # - вилка зп
    # - город

    #
    # for article_tag in article_tags:
    #     h2_tag = article_tag.find('h2')
    #     title = h2_tag.text
    #
    #     time_tag = article_tag.find('time')
    #     time_str = time_tag['datetime']
    #
    #     a_tag = h2_tag.find('a')
    #     link = f'https://habr.com{a_tag["href"]}'
    #
    #     full_article_tag = rq.get(link, headers=headers_data).text
    #     full_article_soup = bs4.BeautifulSoup(full_article_tag,
    #                                           features='lxml')
    #
    #     full_article_tag = full_article_soup.find('div',
    #                                               id='post-content-body')
    #     full_article_text = full_article_tag.text
    #
    #     parsed_article = {
    #         'title': title,
    #         'time': time_str,
    #         'link': link,
    #         'text': full_article_text,
    #     }
    #     parsed_articles.append(parsed_article)
    #
    # # Записать в json информацию о каждой вакансии - ссылка, вилка зп, название компании, город.
    # output = []
    # for article in parsed_articles:
    #     if is_text_match(article['title']) is not None:
    #         output.append(article['time'][0:10] + ' - ' +
    #                       article['title'] + ' - ' +
    #                       article['link'] +
    #                       f' ("{is_text_match(article["title"])}" in title)'
    #                       )
    #     elif is_text_match(article['text']) is not None:
    #         output.append(article['time'][0:10] + ' - ' +
    #                       article['title'] + ' - ' +
    #                       article['link'] +
    #                       f' ("{is_text_match(article["text"])}" in text)'
    #                       )
    #
    # for line in output:
    #     print(line)
