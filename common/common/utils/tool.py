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
from common.core.config import OUTPUT_PATH, graph

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
        if graph:
            try:
                nodes = graph.run(query, entity=entity).data()
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
    """检索相关论文并提取领域实体，支持严格回退到摘要抽取
    
    参数:
    - topic: 主题名称
    - max_paper_num: 最大论文数量
    - compression: 是否进行论文内容压缩
    - user_id: 用户标识
    - task: 任务对象（用于目录归档）
    
    返回:
    - (keynum, relatedPaper, keyword_str): 关键词计数、相关论文列表、关键词说明字符串
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
        # 记录论文基本信息
        try:
            relatedPaper.append({"title": paper["title"], "abstract": paper["abstract"], "compression_result": compression_result})
        except Exception:
            continue
        # 优先使用论文关键词；若缺失则严格回退到摘要实体抽取
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
    """从 Markdown 文件中严格提取指定分节内容
    
    参数:
    - file: 输入 Markdown 文件路径
    - split_section: 目标分节标题关键字（严格匹配）
    
    返回:
    - (text, problem_statement): 原始文本与分节内容（严格匹配失败则抛出异常）
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
    """针对指定分节内容进行技术实体抽取并评分排序
    
    参数:
    - file: 输入 Markdown 文件路径
    - split_section: 目标分节标题关键字（严格匹配）
    
    返回:
    - (sorted_entities, text): 排序后的实体列表与原始文本
    """
    text, problem_statement = extract_message(file, split_section)
    system_prompt = extract_tec_entities_prompt()
    Keywords = call_with_deepseek_jsonout(system_prompt=system_prompt, question=f'The content is: {problem_statement}')['keywords']
    sorted_entities = SearchKeyWordScore(Keywords)
    return sorted_entities, text

def extract_message_review(file, split_section):
    """从评审 Markdown 中严格抽取指定分节并结构化解析
    
    参数:
    - file: 输入 Markdown 文件路径
    - split_section: 目标分节标题关键字（严格匹配）
    
    返回:
    - (text, result): 原始文本与结构化解析结果（严格匹配失败则抛出异常）
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
    """执行评审机制，生成评审文件并解析优化关键词
    
    参数:
    - topic: 主题名称
    - draft: 草案内容
    - user_id: 用户标识
    - task: 任务对象（用于目录归档）
    
    返回:
    - keywords: 从评审结果提取的优化关键词列表
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
    """从 MoA 评审 Markdown 中严格抽取指定分节并返回行列表
    
    参数:
    - file: 输入 Markdown 文件路径
    - split_section: 目标分节标题关键字（严格匹配）
    
    返回:
    - (text, problem_statement): 原始文本与分节内容的行列表（严格匹配失败则抛出异常）
    """
    text = read_markdown_file(file)
    if not split_section:
        raise ValueError("split_section must be non-empty")
    match = re.search(fr'(#.*{split_section}\**\:*)(.*?)(?=#|\Z|---)', text, re.DOTALL)
    if not match:
        raise ValueError(f"Section '{split_section}' not found in file: {file}")
    problem_statement = match.group(2).strip().split('\n')
    return text, problem_statement
