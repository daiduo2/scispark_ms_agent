from .tpl import tpl_env

def get_related_keyword_prompt(Keyword):
    template = tpl_env.get_template("prompt/get_related_keyword_prompt.tpl")
    return template.render(Keyword=Keyword)

def llm_base_prompt():
    llm_base_prompt = "You are a research expert whose primary goal is to identify promising, new, and key scientific problems based on existing scientific literature, in order to aid researchers in discovering novel and significant research opportunities that can advance the field."
    return llm_base_prompt

def fact_extraction_prompt():
    template = tpl_env.get_template("prompt/fact_extraction_prompt.tpl")
    return template.render()

def hypothesis_generate_prompt(Keyword, Known_Information):
    template = tpl_env.get_template("prompt/hypothesis_generate_prompt.tpl")
    return template.render(Keyword=Keyword, Known_Information=Known_Information)

def hypotheses_prompt(Hypotheses):
    hypotheses_index = 0
    hypotheses_prompt = ""
    for hypothesis in Hypotheses:
        hypotheses_index += 1
        hypotheses_prompt += f"\nHypothesis {hypotheses_index}: {hypothesis}"
    return hypotheses_index, hypotheses_prompt

def paper_compression_prompt():
    template = tpl_env.get_template("prompt/paper_compression_prompt.tpl")
    return template.render()

def extract_entity_prompt():
    template = tpl_env.get_template("prompt/extract_entity_prompt.tpl")
    return template.render()

def initial_idea_prompt(hypotheses_prompt, title_abstract_prompt, keyword_str, hypotheses_index, index, keynum):
    template = tpl_env.get_template("prompt/initial_idea_prompt.tpl")
    data = {
        "hypotheses_prompt": hypotheses_prompt,
        "title_abstract_prompt": title_abstract_prompt,
        "keyword_str": keyword_str,
        "hypotheses_index": hypotheses_index,
        "index": index,
        "keynum": keynum,
    }
    return template.render(**data)

def extract_tec_entities_prompt():
    template = tpl_env.get_template("prompt/extract_tec_entities_prompt.tpl")
    return template.render()

def technical_optimizatio_prompt(title, title_abstract_prompt, Initial_Idea_Result):
    template = tpl_env.get_template("prompt/technical_optimizatio_prompt.tpl")
    data = {
        "title": title,
        "title_abstract_prompt": title_abstract_prompt,
        "Initial_Idea_Result": Initial_Idea_Result,
    }
    return template.render(**data)

def review_mechanism_prompt():
    template = tpl_env.get_template("prompt/review_mechanism_prompt.tpl")
    return template.render()

def MoA_based_optimization_prompt(target_next_optimization, optimization_keywords, title_abstract_prompt, draft):
    template = tpl_env.get_template("prompt/MoA_based_optimization_prompt.tpl")
    data = {
        "target_next_optimization": target_next_optimization,
        "optimization_keywords": optimization_keywords,
        "title_abstract_prompt": title_abstract_prompt,
        "draft": draft,
    }
    return template.render(**data)

def human_ai_collaboration_prompt(target_next_optimization, optimization_keywords, title_abstract_prompt, draft):
    template = tpl_env.get_template("prompt/human_ai_collaboration_prompt.tpl")
    data = {
        "target_next_optimization": target_next_optimization,
        "optimization_keywords": optimization_keywords,
        "title_abstract_prompt": title_abstract_prompt,
        "draft": draft,
    }
    return template.render(**data)

