import uuid
from scispark_ms_skills.common.workflow import Initial_Idea

class SimpleTask:
    def __init__(self, task_id=None):
        self.request = {"id": task_id or str(uuid.uuid4())}

def run(topic: str, search_paper_num: int = 5, compression: bool = True, user_id: str = "skill_user"):
    task = SimpleTask()
    result_file = Initial_Idea(Keyword=topic, SearchPaperNum=search_paper_num, Compression=compression, user_id=user_id, task=task)
    return {"result_file": result_file, "task_id": task.request["id"], "user_id": user_id}

