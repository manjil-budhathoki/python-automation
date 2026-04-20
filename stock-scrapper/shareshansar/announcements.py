import re
from .base import BaseScraper

class AnnouncementScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.url = 'https://www.sharesansar.com/company-announcements'

    def _clean_html(self, raw_html):
        return re.sub('<.*?>', '', raw_html).strip() if raw_html else ""

    def _get_payload(self, company_id, start, length):
        return {
            'draw': '1', 'start': str(start), 'length': str(length), 'company': str(company_id),
            'columns[0][data]': 'published_date', 'columns[1][data]': 'title'
        }

    def fetch(self, company_id):
        data = self._post_paginated(self.url, company_id, self._get_payload)
        for item in data: item['title'] = self._clean_html(item.get('title', ''))
        return data