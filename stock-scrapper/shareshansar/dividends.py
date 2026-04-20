from .base import BaseScraper

class DividendScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.url = 'https://www.sharesansar.com/company-dividend'

    def _get_payload(self, company_id, start, length):
        # Base payload
        data = {
            'draw': '1', 
            'start': str(start), 
            'length': str(length), 
            'company': str(company_id),
            'search[value]': '',
            'search[regex]': 'false'
        }
        
        # ShareSansar's Dividend API is very picky. 
        # It needs these exact column definitions to return data.
        cols = [
            'DT_Row_Index', 'bonus_share', 'cash_dividend', 'total_dividend', 
            'announcement_date', 'bookclose_date', 'distribution_date', 
            'bonus_listing_date', 'year'
        ]
        
        for i, col in enumerate(cols):
            data[f'columns[{i}][data]'] = col
            data[f'columns[{i}][name]'] = ''
            data[f'columns[{i}][searchable]'] = 'false'
            data[f'columns[{i}][orderable]'] = 'false'
            data[f'columns[{i}][search][value]'] = ''
            data[f'columns[{i}][search][regex]'] = 'false'
            
        return data

    def fetch(self, company_id):
        # This will now return the full list of dividends
        return self._post_paginated(self.url, company_id, self._get_payload)