import json
import tiktoken
from common.core.prompt import llm_base_prompt
from common.core.config import settings
import dashscope
from http import HTTPStatus
from openai import OpenAI

TOKEN_PRICE_USD = 0.0001
total_tokens_used = 0

def calculate_token_cost(content, model_name="gpt-3.5-turbo"):
    enc = tiktoken.encoding_for_model(model_name)
    tokens = enc.encode(content)
    token_count = len(tokens)
    cost_usd = token_count * TOKEN_PRICE_USD
    global total_tokens_used
    total_tokens_used += token_count
    return token_count, cost_usd

def call_with_deepseek(question, system_prompt=llm_base_prompt(), temperature=0.7):
    client = OpenAI(api_key=settings.DEEPSEEK_API_TOKEN, base_url=settings.DEEPSEEK_API_BASE_URL)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    response = client.chat.completions.create(model="deepseek-chat", temperature=temperature, messages=messages)
    calculate_token_cost(content=question + system_prompt + response.choices[0].message.content)
    return response.choices[0].message.content

def call_with_deepseek_jsonout(system_prompt, question):
    client = OpenAI(api_key=settings.DEEPSEEK_API_TOKEN, base_url=settings.DEEPSEEK_API_BASE_URL)
    if system_prompt == "":
        system_prompt = "The user will provide some exam text. Please parse the \"question\" and \"answer\" and output them in JSON format.\nEXAMPLE INPUT:\nWhich is the highest mountain in the world? Mount Everest.\nEXAMPLE JSON OUTPUT:{\n    \"question\": \"Which is the highest mountain in the world?\",\n    \"answer\": \"Mount Everest\"\n}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    response = client.chat.completions.create(model="deepseek-chat", messages=messages, response_format={'type': 'json_object'})
    calculate_token_cost(content=question + system_prompt + response.choices[0].message.content)
    return json.loads(response.choices[0].message.content)

def call_with_qwenmax(question, system_prompt=llm_base_prompt()):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    responses = dashscope.Generation.call(
        model="qwen-max-2025-01-25",
        api_key=settings.QWEN_API_TOKEN,
        messages=messages,
        stream=False,
        result_format='message',
        top_p=0.8,
        temperature=0.7,
        enable_search=False,
        timeout=600
    )
    if responses.status_code != HTTPStatus.OK:
        raise RuntimeError(f"dashscope error {responses.status_code} {responses.code} {responses.message}")
    return responses.output.choices[0].message.content
