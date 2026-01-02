import json
import re
import time
import requests
from scispark_ms_skills.common.core.config import Proxies

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def get_description(text):
    descriptions = []
    try:
        for item in text['search']:
            descriptions.append(item['description'])
    except:
        pass
    return descriptions

def get_wikipedia_intro(entity_data, lang):
    wikipedia_intro = ''
    if 'sitelinks' in entity_data and f'{lang}wiki' in entity_data['sitelinks']:
        wikipedia_title = entity_data['sitelinks'][f'{lang}wiki']['title']
        wikipedia_url = 'https://en.wikipedia.org/w/api.php' if lang == 'en' else 'https://zh.wikipedia.org/w/api.php'
        wikipedia_params = {
            'action': 'query',
            'format': 'json',
            'titles': wikipedia_title,
            'prop': 'extracts',
            'exintro': True,
            'explaintext': True,
            'converttitles': True
        }
        while True:
            try:
                wikipedia_response = requests.get(wikipedia_url, wikipedia_params)
                break
            except requests.exceptions.RequestException:
                time.sleep(60)
        wikipedia_data = wikipedia_response.json()
        page_id = next(iter(wikipedia_data['query']['pages']))
        wikipedia_intro = wikipedia_data['query']['pages'][page_id]['extract']
        wikipedia_intro = remove_html_tags(wikipedia_intro)
    return wikipedia_intro

def search(query, language='en', limit=3):
    url = "https://www.wikidata.org/w/api.php"
    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'search': {query},
        'language': {language},
        'type': 'item',
        'limit': {limit}
    }
    get = requests.get(url=url, params=params, proxies=Proxies)
    re_json = get.json()
    return re_json

def search_detailed(id, language='en'):
    url = "https://www.wikidata.org/w/api.php"
    params = {
        'ids': {id},
        'action': 'wbgetentities',
        'format': 'json',
        'language': {language},
    }
    get = requests.get(url=url, params=params, proxies=Proxies)
    re_json = get.json()
    return re_json

