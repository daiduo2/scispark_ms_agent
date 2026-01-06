import json
import os
import re
import arxiv
import requests
from bs4 import BeautifulSoup
import urllib.parse
from scihub_cn.scihub import SciHub
from common.core.config import OUTPUT_PATH, Proxies

def check_pdf(file_path):
    try:
        with open(file_path, 'rb') as f:
            header = f.read(5)
            if header != b'%PDF-':
                return False
            return True
    except Exception:
        return False

def sanitize_folder_name(folder_name):
    illegal_chars = r'<>:"/\\\|\?*'
    sanitized_name = re.sub(f'[{illegal_chars}]', '_', folder_name)
    return sanitized_name

def search_google_scholar(doi):
    search_url = f"https://scholar.google.com/scholar?q={urllib.parse.quote(doi)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(search_url, headers=headers, proxies=Proxies)
    soup = BeautifulSoup(response.text, 'html.parser')
    pdf_links = []
    for link in soup.find_all('a'):
        if '[PDF]' in link.get_text():
            pdf_links.append(link['href'])
    for pdf_link in pdf_links:
        return pdf_link

def download_pdf_from_google(pdf_url, title, output_path):
    save_path = f"{output_path}/{title}.pdf"
    response = requests.get(pdf_url, stream=True, proxies=Proxies)
    response.raise_for_status()
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return save_path

def download_pdf_from_scihub(doi, output_path):
    sh = SciHub(proxy=Proxies)
    try:
        save_path = sh.download({"doi": doi}, destination=output_path, is_translate_title=False)
    except:
        save_path = None
    return save_path

def download_pdf_from_unpaywall(doi, title, output_path, email="z1041264242@gmail.com"):
    api_url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
    response = requests.get(api_url, proxies=Proxies)
    if response.status_code == 200:
        data = response.json()
        oa_location = data.get("best_oa_location")
        if oa_location and oa_location.get("url_for_pdf"):
            pdf_url = oa_location["url_for_pdf"]
            pdf_data = requests.get(pdf_url)
            if pdf_data.status_code == 200:
                file_name = f"{title}.pdf"
                file_path = os.path.join(output_path, file_name)
                with open(file_path, "wb") as f:
                    f.write(pdf_data.content)
                return file_path
    return None

def download_pdf_from_arxiv(doi, title, output_path):
    search_engine = arxiv.Search(query=title, max_results=1, sort_by=arxiv.SortCriterion.Relevance)
    for result in search_engine.results():
        pdf_url = result.pdf_url
        pdf_doi = result.doi
        if pdf_doi == doi:
            with requests.get(pdf_url, proxies=Proxies, stream=True) as r:
                if r.status_code == 200:
                    file_name = f"{title}.pdf"
                    file_path = os.path.join(output_path, file_name)
                    with open(file_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    return file_path
    return None

def download_pdf_from_crossref(doi, title, output_path):
    url = f"https://api.crossref.org/works/{doi}"
    headers = {"Accept": "application/json"}
    r = requests.get(url, headers=headers, proxies=Proxies)
    if r.status_code == 200:
        data = r.json()
        for link in data["message"].get("link", []):
            if link.get("content-type") == "application/pdf":
                pdf_url = link["URL"]
                pdf_data = requests.get(pdf_url)
                if pdf_data.status_code == 200:
                    file_name = f"{title}.pdf"
                    file_path = os.path.join(output_path, file_name)
                    with open(file_path, "wb") as f:
                        f.write(pdf_data.content)
                    return file_path
    return None

def getdown_pdf_google_url(doi, title, output_path):
    pdf_url = search_google_scholar(doi)
    if pdf_url:
        save_path = download_pdf_from_google(pdf_url, title, output_path)
        return save_path
    return False

def download_pdf_from_Giiisp(doi, title, output_path):
    url = "https://giiisp.com/first/oaPaper/api/filter"
    payload = {"count": 5, "sortOrder": 1, "sortBy": 1, "searchQuery": title, "searchType": 1}
    headers = {"Content-Type": "application/json", "Authorization": "85d7e5806950935fa3bf11f8e017c38f", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        if result['data'] != [] and result['data'][0]['giiispPdfUrl'] is not None:
            pattern = r"https?://(dx\.)?doi\.org/"
            pdf_url = result['data'][0]['giiispPdfUrl']
            pdf_doi = re.sub(pattern, "", result['data'][0]['doi'])
            if pdf_doi == doi:
                pdf_data = requests.get(pdf_url)
                if pdf_data.status_code == 200:
                    file_name = f"{title}.pdf"
                    file_path = os.path.join(output_path, file_name)
                    with open(file_path, "wb") as f:
                        f.write(pdf_data.content)
                    return file_path
        return None
    except requests.exceptions.RequestException:
        return None
    except json.JSONDecodeError:
        return None

def download_pdf(doi, title, output_path):
    download_methods = [
        lambda: download_pdf_from_arxiv(doi, title, output_path),
        lambda: download_pdf_from_Giiisp(doi, title, output_path),
        lambda: download_pdf_from_unpaywall(doi, title, output_path),
        lambda: getdown_pdf_google_url(doi, title, output_path),
        lambda: download_pdf_from_scihub(doi, output_path),
    ]
    for method in download_methods:
        result = method()
        if result and check_pdf(result):
            return result
    return None

def download_all_pdfs(dois, title, topic, user_id, task):
    task_id = getattr(task, 'request', {}).get('id', 'default_task_id') if task else 'default_task_id'
    output_path = fr"{OUTPUT_PATH}/{user_id}/{task_id}/{topic}/Paper/pdf"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    paper_pdf = download_pdf(dois, sanitize_folder_name(title), output_path)
    return paper_pdf

