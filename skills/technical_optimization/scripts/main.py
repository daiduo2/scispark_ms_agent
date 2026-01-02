import uuid
from scispark_ms_skills.common.workflow import Technical_Optimization

class SimpleTask:
    def __init__(self, task_id=None):
        self.request = {"id": task_id or str(uuid.uuid4())}

def run(topic: str, initial_idea_result_file: str, compression: bool = True, user_id: str = "skill_user"):
    task = SimpleTask()
    result_file = Technical_Optimization(Keyword=topic, Initial_Idea_Result_File=initial_idea_result_file, Compression=compression, user_id=user_id, task=task)
    return {"result_file": result_file, "task_id": task.request["id"], "user_id": user_id}

