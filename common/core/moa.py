import agentscope
from agentscope import msghub
from agentscope.agents import DialogAgent
from agentscope.message import Msg
from scispark_ms_skills.common.core.config import OUTPUT_PATH, settings
import os
from scispark_ms_skills.common.core.tpl import tpl_env

model_configs = [
    {
        "config_name": "qwen-max-2025-01-25",
        "model_type": "dashscope_chat",
        "model_name": "qwen-max",
        "api_key": settings.QWEN_API_TOKEN,
    }
]

def moa_idea_iteration(topic="", user_prompt="", user_id="", task=None):
    task_id = getattr(task, 'request', {}).get('id', 'default_task_id') if task else 'default_task_id'
    file_path_prefix = fr"{OUTPUT_PATH}/{user_id}/{task_id}/{topic}/MOA"
    agentscope.init(model_configs=model_configs, save_api_invoke=True, save_log=True)
    system_prompt = (
        "You are a research expert whose primary goal is to identify promising, new, and key scientific problems "
        "based on existing scientific literature, in order to aid researchers in discovering novel and significant "
        "research opportunities that can advance the field."
    )
    dialogAgent_QwenA = DialogAgent(name="QwenA", model_config_name="qwen-max-2025-01-25", sys_prompt=system_prompt)
    dialogAgent_QwenB = DialogAgent(name="QwenB", model_config_name="qwen-max-2025-01-25", sys_prompt=system_prompt)
    dialogAgent_QwenC = DialogAgent(name="QwenC", model_config_name="qwen-max-2025-01-25", sys_prompt=system_prompt)
    dialogAgent_AC = DialogAgent(name="QwenAC", model_config_name="qwen-max-2025-01-25", sys_prompt=system_prompt)
    dialogAgent_Reviewer = DialogAgent(name="QwenReviewer", model_config_name="qwen-max-2025-01-25", sys_prompt=system_prompt)
    QwenA_message = dialogAgent_QwenA(Msg(name="User", role="user", content=user_prompt))
    QwenB_message = dialogAgent_QwenB(Msg(name="User", role="user", content=user_prompt))
    QwenC_message = dialogAgent_QwenC(Msg(name="User", role="user", content=user_prompt))
    os.makedirs(file_path_prefix, exist_ok=True)
    with open(fr"{file_path_prefix}/QwenA_{topic}_moa.md", 'w', encoding='utf-8') as f:
        f.write(QwenA_message.content)
    with open(fr"{file_path_prefix}/QwenB_{topic}_moa.md", 'w', encoding='utf-8') as f:
        f.write(QwenB_message.content)
    with open(fr"{file_path_prefix}/QwenC_{topic}_moa.md", 'w', encoding='utf-8') as f:
        f.write(QwenC_message.content)
    aggregation_tpl = tpl_env.get_template("prompt/moa/moa_idea_iteration_aggregation.tpl")
    data = {
        "Qwen_message": QwenB_message.content,
        "DeepSeek_message": QwenC_message.content,
        "Gemini_message": QwenA_message.content,
    }
    aggregation = aggregation_tpl.render(data=data)
    AC_message = dialogAgent_AC(Msg(name="User", role="user", content=aggregation))
    with open(fr"{file_path_prefix}/AC_{topic}_moa.md", 'w', encoding='utf-8') as f:
        f.write(AC_message.content)
    reviewer_prompt_tpl = tpl_env.get_template("prompt/moa/reviewer_prompt.tpl")
    Reviewer_prompt = reviewer_prompt_tpl.render()
    Reviewer_message = dialogAgent_Reviewer(Msg(name="User", role="user", content=Reviewer_prompt))
    with open(fr"{file_path_prefix}/Reviewer_{topic}_moa.md", 'w', encoding='utf-8') as f:
        f.write(Reviewer_message.content)
    agentscope.print_llm_usage()
    return AC_message.content

def moa_table(model_configs=model_configs, topic='', draft='', user_id='', task=None):
    task_id = getattr(task, 'request', {}).get('id', 'default_task_id') if task else 'default_task_id'
    file_path_prefix = fr"{OUTPUT_PATH}/{user_id}/{task_id}/{topic}/MOA"
    agentscope.init(model_configs=model_configs, save_api_invoke=True, save_log=True)
    role = (
        "You are a seminar reviewer responsible for evaluating research idea drafts. When reviewing, take into "
        "account the content of the draft as well as feedback from other reviewers. While recognizing the value "
        "in others' comments, your focus should be on providing a unique perspective that enhances and optimizes "
        "the draft. Your feedback should be concise, consisting of a well-constructed paragraph that builds on "
        "the ongoing discussion without replicating other reviewers' suggestions. Always strive to present your "
        "distinct viewpoint."
    )
    viewer = """Act a moderator in a seminar.  After the four reviewers have completed their evaluations, 
    you will need to comprehensively analyze the content of the idea draft as well as the valuable review comments 
    provided by each reviewer. Based on this, you are required to systematically summarize and integrate these review 
    opinions, ensuring that all key feedback and suggestions are accurately and comprehensively considered. The 
    output should strictly follow the format below: # Overall Opinions:
    
    # Iterative Optimization Search Keywords:
    - [Keyword 1]
    - [Keyword 2]
    - ..."""
    dialogAgent_Qwen1 = DialogAgent(name="Reviewer 1", model_config_name="qwen-max-2025-01-25", sys_prompt=role)
    dialogAgent_Qwen2 = DialogAgent(name="Reviewer 2", model_config_name="qwen-max-2025-01-25", sys_prompt=role)
    dialogAgent_Qwen3 = DialogAgent(name="Reviewer 3", model_config_name="qwen-max-2025-01-25", sys_prompt=role)
    dialogAgent_Viewer = DialogAgent(name="Viewer", model_config_name="qwen-max-2025-01-25", sys_prompt=viewer)
    with msghub(participants=[dialogAgent_Qwen1, dialogAgent_Qwen2, dialogAgent_Qwen3, dialogAgent_Viewer]) as hub:
        hub.broadcast(Msg(name="Host", role="user", content=f"Welcome to join the seminar chat! Now, The idea draft we need to discuss as follows:\n{draft}"))
        dialogAgent_Qwen1()
        dialogAgent_Qwen2()
        dialogAgent_Qwen3()
        viewer_message = dialogAgent_Viewer()
    with open(fr"{file_path_prefix}/{topic}_review_moa.md", 'w', encoding='utf-8') as f:
        f.write(viewer_message.content)
    agentscope.print_llm_usage()

