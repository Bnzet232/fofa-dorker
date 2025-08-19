# FOFA Dorking Tool

# This script is designed to interact with the FOFA API to conduct dorking tasks.

import requests

class FofaDorker:
    def __init__(self, email, key):
        self.email = email
        self.key = key
        self.base_url = 'https://fofa.so/api/v1'

    def search(self, query):
        url = f'{self.base_url}/search/result'
        params = {'query': query, 'email': self.email, 'key': self.key}
        response = requests.get(url, params=params)
        return response.json()

# Example usage:
# fofa_dorker = FofaDorker(email='your_email', key='your_key')
# results = fofa_dorker.search('example query')
# print(results)