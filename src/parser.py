import re
from collections import namedtuple
from datetime import datetime

import requests
from bs4 import BeautifulSoup, ResultSet
from loguru import logger

from config import BASE_URL


Post = namedtuple('Post', field_names=['date', 'title', 'link'])


class Parser:
    DEFAULT_TIMEOUT = 3

    def __init__(self) -> None:
        self.base_url = BASE_URL
        self.session = requests.Session()

    def get_latest_post(self):
        return self.get_posts(limit=1)[0]

    def get_posts(self, limit: int = 10):
        url = f'{self.base_url}/ru/news/obyavleniya'
        response = self._perform_request('get', url)
        posts = self._find_all_posts(response.text)[:limit]

        if not posts:
            return

        return self._normalize_posts(posts)

    @logger.catch
    def _perform_request(self, method: str, url: str, **kwargs):
        timeout = kwargs.pop('timeout', self.DEFAULT_TIMEOUT)
        response = getattr(self.session, method)(url, timeout=timeout, **kwargs)
        response.raise_for_status()

        return response

    @logger.catch
    def _find_all_posts(self, html_text: str) -> ResultSet:
        soup = BeautifulSoup(html_text, 'html.parser')

        posts = soup.find_all('div', class_='posts__item')
        return posts

    @logger.catch
    def _normalize_posts(self, posts: ResultSet):
        normalized_posts = []
        for post in posts:
            post_info = post.find('div', class_='posts__info')
            text = ' '.join(post_info.text.split())
            title, date = self._extract_title_and_date(text)
            link = post_info.find('a').attrs['href']
            normalized_posts.append(Post(date, title, f'{self.base_url}{link}'))

        return normalized_posts

    @logger.catch
    def _extract_title_and_date(self, text: str):
        pattern = r'([0-9]{2}.[0-9]{2}.[0-9]{4})'
        date = re.search(pattern, text).group()
        title = re.sub(pattern, '', text).strip()
        return title, datetime.strptime(date, '%d.%m.%Y').date()


parser = Parser()
