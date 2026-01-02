from scispark_ms_skills.common.core.config import MinerU_Token, OUTPUT_PATH
import re
import time
import zipfile
import pandas as pd
import requests
import os

def download_zip_file(url, zip_save_path):
    response = requests.get(url, timeout=600)
    if response.status_code == 200:
        with open(zip_save_path, 'wb') as file:
            file.write(response.content)

def find_md_files_in_zip(zip_path, copy_path, batch_id):
    md_files = []
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith('.md'):
                md_files.append(file)
        for idx, md_file in enumerate(md_files, start=1):
            extracted_path = zip_ref.extract(md_file, copy_path)
            new_file_path = os.path.join(copy_path, f"{batch_id.rstrip('.md')}_{idx}.md")
            os.replace(extracted_path, new_file_path)
    return md_files

def extract_pdf_name(path):
    match = re.search(r"([^\\]+)\.pdf$", path, re.IGNORECASE)
    if match:
        pdf_name = match.group(1)
        return pdf_name
    return None

def download_file_mineruapi(batch_id, topic, user_id, task, max_wait_seconds=3600, poll_interval_seconds=5):
    task_id = getattr(task, 'request', {}).get('id', 'default_task_id') if task else 'default_task_id'
    file_path_prefix = fr"{OUTPUT_PATH}/{user_id}/{task_id}/{topic}/Paper"
    start_ts = time.time()
    token = MinerU_Token
    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    while True:
        if time.time() - start_ts > max_wait_seconds:
            return False
        url = f'https://mineru.net/api/v4/extract-results/batch/{batch_id}'
        res = requests.get(url, headers=header, timeout=600)
        data = res.json()
        state = data["data"]["extract_result"][0]["state"]
        if state == "done":
            directory = fr"{file_path_prefix}/markdown"
            zip_dir = fr"{file_path_prefix}/zip"
            os.makedirs(directory, exist_ok=True)
            os.makedirs(zip_dir, exist_ok=True)
            download_zip_file(url=data["data"]["extract_result"][0]["full_zip_url"], zip_save_path=zip_dir + fr"/{batch_id}.zip")
            find_md_files_in_zip(zip_path=zip_dir + f"/{batch_id}.zip", copy_path=directory, batch_id=f"{batch_id}.md")
            return True
        elif state in ("waiting-file", "running"):
            time.sleep(poll_interval_seconds)
            continue
        else:
            return False

def pdf2md_mineruapi(file_path, topic, user_id, task):
    task_id = getattr(task, 'request', {}).get('id', 'default_task_id') if task else 'default_task_id'
    down_history = fr"{OUTPUT_PATH}/{user_id}/{task_id}/{topic}/down_history.xlsx"
    os.makedirs(os.path.dirname(down_history), exist_ok=True)
    if not os.path.exists(down_history):
        pd.DataFrame().to_excel(down_history, index=False)
    df = pd.read_excel(down_history)
    pdf_name = extract_pdf_name(path=file_path)
    for index, row in df.iterrows():
        if row['Paper'] == pdf_name:
            download_file_mineruapi(batch_id=row['Batch_ID'], topic=topic, user_id=user_id, task=task)
            return row['Batch_ID']
    url = 'https://mineru.net/api/v4/file-urls/batch'
    token = MinerU_Token
    header = {'Content-Type': 'application/json', 'Authorization': f"Bearer {token}"}
    data = {"enable_formula": True, "language": "en", "layout_model": "doclayout_yolo", "enable_table": True, "files": [{"name": file_path, "is_ocr": True, "data_id": "abcd"}]}
    try:
        response = requests.post(url, headers=header, json=data, timeout=600)
        if response.status_code == 200:
            result = response.json()
            if result["code"] == 0:
                batch_id = result["data"]["batch_id"]
                urls = result["data"]["file_urls"]
                with open(file_path, 'rb') as f:
                    res_upload = requests.put(urls[0], data=f, timeout=600)
                if res_upload.status_code != 200:
                    return 0
                download_file_mineruapi(batch_id=batch_id, topic=topic, user_id=user_id, task=task)
                new_row = {'Paper': pdf_name, 'Batch_ID': batch_id}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_excel(down_history, index=False)
                return batch_id
    except Exception:
        pass
    return 0

