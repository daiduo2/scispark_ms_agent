import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")
    MINERU_API_TOKEN: str = ""
    QWEN_API_TOKEN: str = ""
    DEEPSEEK_API_TOKEN: str = ""
    DEEPSEEK_API_BASE_URL: str = "https://api.deepseek.com/v1"
    NEO4J_USERNAME: str = ""
    NEO4J_PASSWORD: str = ""
    NEO4J_HOST: str = ""
    NEO4J_PORT: str = ""
    OUTPUT_PATH: str = "./scispark_ms_skills_output"
    HTTP_PROXY: str = ""
    HTTPS_PROXY: str = ""

settings = Settings()

OUTPUT_PATH = settings.OUTPUT_PATH
MinerU_Token = settings.MINERU_API_TOKEN

def get_proxies():
    proxies = {}
    if settings.HTTP_PROXY:
        proxies['http'] = settings.HTTP_PROXY
    if settings.HTTPS_PROXY:
        proxies['https'] = settings.HTTPS_PROXY
    return proxies

Proxies = get_proxies()

try:
    from py2neo import Graph
    neo4j_url = f"bolt://{settings.NEO4J_HOST}:{settings.NEO4J_PORT}"
    graph = Graph(neo4j_url, auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD))
    graph.run("RETURN 1").data()
except Exception:
    graph = None

