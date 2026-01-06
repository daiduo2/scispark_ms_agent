<<<<<<< HEAD
import os
import re
import time
import ast
from common.core.prompt import get_related_keyword_prompt, paper_compression_prompt, extract_entity_prompt, extract_tec_entities_prompt, review_mechanism_prompt
from common.utils.llm_api import call_with_deepseek, call_with_deepseek_jsonout, call_with_qwenmax
from common.utils.arxiv_api import search_paper
from common.utils.scholar_download import download_all_pdfs
from common.utils.pdf_to_md import pdf2md_mineruapi
from common.utils.wiki_search import get_description, search
from common.core.config import OUTPUT_PATH, get_graph

=======
import os
import re
import time
import ast
from common.core.prompt import get_related_keyword_prompt, paper_compression_prompt, extract_entity_prompt, extract_tec_entities_prompt, review_mechanism_prompt
from common.utils.llm_api import call_with_deepseek, call_with_deepseek_jsonout, call_with_qwenmax
from common.utils.arxiv_api import search_paper
from common.utils.scholar_download import download_all_pdfs
from common.utils.pdf_to_md import pdf2md_mineruapi
from common.utils.wiki_search import get_description, search
from common.core.config import OUTPUT_PATH, get_graph

>>>>>>> e967a4b (ci: run import check as script; pytest ignore duplicate tests; align neo4j password; add script entry)
def SearchKeyWordScore(Keywords):
    for index, keyword in enumerate(Keywords):
        entity = keyword['entity']
        query = """
        MATCH (n:Words)
        WHERE n.other CONTAINS $entity OR n.name = $entity
        RETURN n.count,n
        ORDER BY n.count DESC
        LIMIT 1
        """
        nodes = []
        g = get_graph()
        if g:
            try:
                nodes = g.run(query, entity=entity).data()
            except Exception:
                nodes = []
        if len(nodes) != 0:
            Keywords[index]['count'] = nodes[0]['n.count']
        else:
            Keywords[index]['count'] = 0
    min_count = min(item['count'] for item in Keywords) if Keywords else 0
    max_count = max(item['count'] for item in Keywords) if Keywords else 1
    weight_importance = 0.4
    weight_count = 0.6
    for item in Keywords:
        if max_count == min_count:
            normalized_count = 0.5
        else:
            normalized_count = (item['count'] - min_count) / (max_count - min_count)
        composite_score = (item['importance_score'] * weight_importance) + (normalized_count * weight_count)
        item['composite_score'] = composite_score
    sorted_data = sorted(Keywords, key=lambda x: x['composite_score'], reverse=True)
    return sorted_data

def get_related_keyword(Keyword):
    user_prompt = get_related_keyword_prompt(Keyword=Keyword)
    result = call_with_deepseek(system_prompt="You are a helpful assistant.", question=user_prompt)
    return ast.literal_eval(result)

def remove_number_prefix(paragraph):
    pattern = r'^\d+\. |(?<=\n)\d+\. '
    modified_paragraph = re.sub(pattern, '', paragraph, flags=re.MULTILINE)
    return modified_paragraph

def read_markdown_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except Exception:
        return ""

def extract_hypothesis(file, split_section="Hypothesis"):
    text = read_markdown_file(file)
    pattern = re.compile(fr"{split_section} \d+:(.+?)\n", re.DOTALL)
    matches = pattern.findall(text)
    hypotheses = [match.strip() for match in matches]
    return hypotheses

def paper_compression(doi, title, topic, user_id, task):
    paper_pdf_path = download_all_pdfs(dois=doi, title=title, topic=topic, user_id=user_id, task=task)
    task_id = getattr(task, 'request', {}).get('id', 'default_task_id') if task else 'default_task_id'
    file_path_prefix = fr"{OUTPUT_PATH}/{user_id}/{task_id}/{topic}/Paper"
    directory = fr"{file_path_prefix}/compression"
    batch_id = pdf2md_mineruapi(file_path=paper_pdf_path, topic=topic, user_id=user_id, task=task)
    if batch_id == 0:
        time.sleep(10)
        batch_id = pdf2md_mineruapi(file_path=paper_pdf_path, topic=topic, user_id=user_id, task=task)
    pattern = r'#{0,}\s*References.*'
    if batch_id != 0:
        paper_content = read_markdown_file(file_path=fr"{file_path_prefix}/markdown/{batch_id}.md")
        paper_content = re.sub(pattern, '', paper_content, flags=re.DOTALL | re.IGNORECASE)
    else:
        return 'None'
    system_prompt = paper_compression_prompt()
    compression_result = call_with_qwenmax(question=f"The content is '''{paper_content}'''", system_prompt=system_prompt)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(fr"{directory}/{batch_id}.md", 'w', encoding='utf-8') as f:
        f.write(compression_result)
    return compression_result

def search_releated_paper(topic, max_paper_num=5, compression=True, user_id="", task=None):
    """妫€绱㈢浉鍏宠鏂囧苟鎻愬彇棰嗗煙瀹炰綋锛屾敮鎸佷弗鏍煎洖閫€鍒版憳瑕佹娊鍙?
    
    鍙傛暟:
    - topic: 涓婚鍚嶇О
    - max_paper_num: 鏈€澶ц鏂囨暟閲?
    - compression: 鏄惁杩涜璁烘枃鍐呭鍘嬬缉
    - user_id: 鐢ㄦ埛鏍囪瘑
    - task: 浠诲姟瀵硅薄锛堢敤浜庣洰褰曞綊妗ｏ級
    
    杩斿洖:
    - (keynum, relatedPaper, keyword_str): 鍏抽敭璇嶈鏁般€佺浉鍏宠鏂囧垪琛ㄣ€佸叧閿瘝璇存槑瀛楃涓?
    """
    keynum = 0
    relatedPaper = []
    Entities = []
    papers = search_paper(Keywords=[topic], Limit=max_paper_num)
    for paper in papers:
        if compression:
            try:
                compression_result = paper_compression(doi=paper["doi"], title=paper["title"], topic=topic, user_id=user_id, task=task)
            except Exception:
                compression_result = "None"
        else:
            compression_result = "None"
        # 鐠佹澘缍嶇拋鐑樻瀮閸╃儤婀版穱鈩冧紖
        try:
            relatedPaper.append({"title": paper["title"], "abstract": paper["abstract"], "compression_result": compression_result})
        except Exception:
            continue
        # 娴兼ê鍘涙担璺ㄦ暏鐠佺儤鏋冮崗鎶芥暛鐠囧稄绱遍懟銉у繁婢跺崬鍨稉銉︾壐閸ョ偤鈧偓閸掔増鎲崇憰浣哥杽娴ｆ挻濞婇崣?
        paper_keywords = paper.get("keyword")
        if paper_keywords:
            try:
                for keyword in paper_keywords:
                    Entities.append(keyword)
            except Exception:
                pass
        else:
            try:
                jr = call_with_deepseek_jsonout(system_prompt=extract_entity_prompt(), question=paper.get("abstract", ""))
                extracted = jr.get("keywords", []) if jr else []
                for kw in extracted:
                    Entities.append(kw)
            except Exception:
                pass
    try:
        json_result = call_with_deepseek_jsonout(system_prompt=extract_entity_prompt(), question=f"""The content is: {Entities}.""")
        Keywords = json_result.get('keywords', []) if json_result else []
    except Exception:
        Keywords = []
    keyword_str = ""
    for keyword in Keywords:
        keynum += 1
        temp = get_description(search(query=keyword))
        if not temp:
            keyword_str += f"{keyword};\n"
        else:
            keyword_str += f"{keyword}:{temp[0]};\n"
    return keynum, relatedPaper, keyword_str

def extract_message(file, split_section):
    """浠?Markdown 鏂囦欢涓弗鏍兼彁鍙栨寚瀹氬垎鑺傚唴瀹?
    
    鍙傛暟:
    - file: 杈撳叆 Markdown 鏂囦欢璺緞
    - split_section: 鐩爣鍒嗚妭鏍囬鍏抽敭瀛楋紙涓ユ牸鍖归厤锛?
    
    杩斿洖:
    - (text, problem_statement): 鍘熷鏂囨湰涓庡垎鑺傚唴瀹癸紙涓ユ牸鍖归厤澶辫触鍒欐姏鍑哄紓甯革級
    """
    text = read_markdown_file(file)
    if not split_section:
        raise ValueError("split_section must be non-empty")
    match = re.search(fr'### \S*{split_section}\S*(.*?)(?=###|---|\Z)', text, re.DOTALL)
    if not match:
        raise ValueError(f"Section '{split_section}' not found in file: {file}")
    problem_statement = match.group(1).strip()
    return text, problem_statement

def extract_technical_entities(file, split_section):
    """閽堝鎸囧畾鍒嗚妭鍐呭杩涜鎶€鏈疄浣撴娊鍙栧苟璇勫垎鎺掑簭
    
    鍙傛暟:
    - file: 杈撳叆 Markdown 鏂囦欢璺緞
    - split_section: 鐩爣鍒嗚妭鏍囬鍏抽敭瀛楋紙涓ユ牸鍖归厤锛?
    
    杩斿洖:
    - (sorted_entities, text): 鎺掑簭鍚庣殑瀹炰綋鍒楄〃涓庡師濮嬫枃鏈?
    """
    text, problem_statement = extract_message(file, split_section)
    system_prompt = extract_tec_entities_prompt()
    Keywords = call_with_deepseek_jsonout(system_prompt=system_prompt, question=f'The content is: {problem_statement}')['keywords']
    sorted_entities = SearchKeyWordScore(Keywords)
    return sorted_entities, text

def extract_message_review(file, split_section):
    """浠庤瘎瀹?Markdown 涓弗鏍兼娊鍙栨寚瀹氬垎鑺傚苟缁撴瀯鍖栬В鏋?
    
    鍙傛暟:
    - file: 杈撳叆 Markdown 鏂囦欢璺緞
    - split_section: 鐩爣鍒嗚妭鏍囬鍏抽敭瀛楋紙涓ユ牸鍖归厤锛?
    
    杩斿洖:
    - (text, result): 鍘熷鏂囨湰涓庣粨鏋勫寲瑙ｆ瀽缁撴灉锛堜弗鏍煎尮閰嶅け璐ュ垯鎶涘嚭寮傚父锛?
    """
    text = read_markdown_file(file)
    if not split_section:
        raise ValueError("split_section must be non-empty")
    match = re.search(fr'(#.*{split_section}\**\:*)(.*?)(?=#|\Z|---)', text, re.DOTALL)
    if not match:
        raise ValueError(f"Section '{split_section}' not found in file: {file}")
    problem_statement = match.group(2).strip()
    if split_section == "Iterative Optimization Search Keywords":
        question = f"""Based on the content provided below, extract the next optimization search keywords. Return the 
        result only in the following JSON format. Do not add any explanations or irrelevant information. JSON output 
        format: {{ "optimization_keyword": "xxx", ... }}
        
        Content to extract:
        '''
        #{split_section}\n{problem_statement}
        '''"""
    elif split_section == "Next Steps for Optimization":
        question = f"""Based on the content provided below, extract the next optimization goal. Return the result 
        only in the following JSON format. Do not add any explanations or irrelevant information. JSON output format: 
        {{ "optimization_goal": "xxx", ... }}
        
        Content to extract:
        '''
        #{split_section}\n{problem_statement}
        '''"""
    else:
        question = problem_statement
    result = call_with_deepseek_jsonout(question=question, system_prompt="")
    return text, result

def review_mechanism(topic, draft="", user_id="", task=None):
    """鎵ц璇勫鏈哄埗锛岀敓鎴愯瘎瀹℃枃浠跺苟瑙ｆ瀽浼樺寲鍏抽敭璇?
    
    鍙傛暟:
    - topic: 涓婚鍚嶇О
    - draft: 鑽夋鍐呭
    - user_id: 鐢ㄦ埛鏍囪瘑
    - task: 浠诲姟瀵硅薄锛堢敤浜庣洰褰曞綊妗ｏ級
    
    杩斿洖:
    - keywords: 浠庤瘎瀹＄粨鏋滄彁鍙栫殑浼樺寲鍏抽敭璇嶅垪琛?
    """
    system_prompt = review_mechanism_prompt()
    user_prompt = f"""# Idea Draft\n{draft}"""
    result = call_with_qwenmax(system_prompt=system_prompt, question=user_prompt)
    task_id = getattr(task, 'request', {}).get('id', 'default_task_id') if task else 'default_task_id'
    file_path_prefix = fr"{OUTPUT_PATH}/{user_id}/{task_id}/{topic}/Review"
    os.makedirs(file_path_prefix, exist_ok=True)
    with open(fr"{file_path_prefix}/{topic}_review.md", 'w', encoding='utf-8') as f:
        f.write(result)
    text, optimize_messages = extract_message_review(file=fr"{file_path_prefix}/{topic}_review.md", split_section="Iterative Optimization Search Keywords")
    keywords = []
    for optimize_message in optimize_messages.values():
        keywords.append({'keyword': optimize_message})
    return keywords

def extract_message_review_moa(file, split_section):
    """浠?MoA 璇勫 Markdown 涓弗鏍兼娊鍙栨寚瀹氬垎鑺傚苟杩斿洖琛屽垪琛?
    
    鍙傛暟:
    - file: 杈撳叆 Markdown 鏂囦欢璺緞
    - split_section: 鐩爣鍒嗚妭鏍囬鍏抽敭瀛楋紙涓ユ牸鍖归厤锛?
    
    杩斿洖:
    - (text, problem_statement): 鍘熷鏂囨湰涓庡垎鑺傚唴瀹圭殑琛屽垪琛紙涓ユ牸鍖归厤澶辫触鍒欐姏鍑哄紓甯革級
    """
    text = read_markdown_file(file)
    if not split_section:
        raise ValueError("split_section must be non-empty")
    match = re.search(fr'(#.*{split_section}\**\:*)(.*?)(?=#|\Z|---)', text, re.DOTALL)
    if not match:
        raise ValueError(f"Section '{split_section}' not found in file: {file}")
    problem_statement = match.group(2).strip().split('\n')
    return text, problem_statement
