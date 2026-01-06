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

graph = None
_graph_inited = False
def get_graph():
    """鑾峰彇Neo4j杩炴帴瀹炰緥锛岄噰鐢ㄦ儼鎬у垵濮嬪寲骞跺け璐ュ畨鍏?    
    杩斿洖:
    - Graph 鎴?None锛氬綋鐜鍙橀噺缂哄け鎴栬繛鎺ュけ璐ユ椂杩斿洖 None锛屼笉鎶涘嚭寮傚父
    """
    global graph, _graph_inited
    if _graph_inited and graph is not None:
        return graph
    _graph_inited = True
    try:
        from py2neo import Graph
        host = settings.NEO4J_HOST.strip()
        port = str(settings.NEO4J_PORT).strip()
        user = settings.NEO4J_USERNAME
        password = settings.NEO4J_PASSWORD
        if not host or not port:
            graph = None
            return graph
        neo4j_url = f"bolt://{host}:{port}"
        g = Graph(neo4j_url, auth=(user, password))
        try:
            g.run("RETURN 1").data()
            graph = g
        except Exception:
            graph = None
    except Exception:
        graph = None
    return graph

