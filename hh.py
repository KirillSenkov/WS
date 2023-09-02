import requests as rq
import bs4

# import lxml
from fake_headers import Headers
from pprint import pprint as pp

if __name__ == "__main__":
    headers = Headers(browser="firefox", os="win")
    headers_data = headers.generate()

    main_page_html = rq.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2',
                            headers=headers_data).text

    main_page_soup = bs4.BeautifulSoup(main_page_html, "lxml")

    div_article_list_tag = main_page_soup.find("div",
                                               class_="tm-articles-list")
    article_tags = div_article_list_tag.find_all("article")

    parsed_articles = []

    for article_tag in article_tags:
        h2_tag = article_tag.find("h2")
        title = h2_tag.text

        time_tag = article_tag.find("time")
        time_str = time_tag["datetime"]

        a_tag = h2_tag.find("a")
        link = f'https://habr.com{a_tag["href"]}'

        full_article_tag = rq.get(link, headers=headers_data).text
        full_article_soup = bs4.BeautifulSoup(full_article_tag,
                                              features="lxml")

        full_article_tag = full_article_soup.find("div",
                                                  id=l"post-content-body")
        full_article_text = full_article_tag.text

        parsed_article = {
            "title": title,
            "time": time_str,
            "link": link,
            "text": full_article_text,
        }
        parsed_articles.append(parsed_article)

    pp(parsed_articles)
