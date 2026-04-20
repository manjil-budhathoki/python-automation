import requests
import time

class BaseScraper:
    def __init__(self):
        # Update these if they expire
        self.cookies = {
            'XSRF-TOKEN': 'eyJpdiI6InZEc0MrZ0U3cXBlbE1JMTgxYmlqaUE9PSIsInZhbHVlIjoieGlXMGswRk01UDBwRHlVNjZPeG1xM016YUFMbTI1UjFyTnBmQ2IxVHBHc2g0RXRuQkVpaExFYnlxbDRNaC9VU2k3L29IaTAxQTJtSlp5T21FeUJIWnlkMWluQ2VQMjhGeU9adTZKSjNLYmp3RkFXT3o0b2Vhd3BFOFB5Rms1NmgiLCJtYWMiOiIxMTY2MWQ4YzhiODNmYWRmZGVkZWY3ZDM0ZTVmMjE0NGUyNWFhMGM4ZTUwODgzODJkYWU2ZGNlZGU3YjU3OTA0In0%3D',
            'sharesansar_session': 'eyJpdiI6IjBDVzNwRGNxaDJqZGk0cXJFYnpXQVE9PSIsInZhbHVlIjoiME9XakpPVWhjMkp2M0hmSUFpd3hzOGlxMThxalNiMy9HdUpyUThhZnBvbTI1dytFbFVnamZNMUtQcjRRbTM1Z3RZejlrdXlHWFVzYVMyVmI3OUx3cm53RVhWRlJDK2RQaEFpMCtNZmRSbE4xOG84TGVuM0ZpekFKa2E4cmVhb2siLCJtYWMiOiIyZjM0OTAxZjI0N2U4ZTQ0YWI2YzgzZTE2NTQxZjc0Y2JjYmYzNjAxNmM4ZjQ2NDI4NDA5YmJiNGU5MWQ4YTU5In0%3D',
        }
        self.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.sharesansar.com',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
            'x-csrf-token': 'ROT77nhvEyZWqAtLa39xLrc9UqXzSBmBFKTUaQP5',
            'x-requested-with': 'XMLHttpRequest',
        }

    def _post_paginated(self, url, company_id, payload_func, page_size=50):
        all_data = []
        start = 0
        while True:
            payload = payload_func(company_id, start, page_size)
            response = requests.post(url, cookies=self.cookies, headers=self.headers, data=payload, timeout=15)
            if response.status_code != 200: break
            json_res = response.json()
            rows = json_res.get('data', [])
            all_data.extend(rows)
            if start + page_size >= json_res.get('recordsTotal', 0): break
            start += page_size
            time.sleep(0.1)
        return all_data