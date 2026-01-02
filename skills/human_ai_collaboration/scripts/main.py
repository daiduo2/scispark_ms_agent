import uuid
from scispark_ms_skills.common.workflow import Human_AI_Collaboration

class SimpleTask:
    def __init__(self, task_id=None):
        self.request = {"id": task_id or str(uuid.uuid4())}

def run(topic: str, moa_based_optimization_result_file: str, compression: bool = True, user_id: str = "skill_user"):
    task = SimpleTask()
    result_file = Human_AI_Collaboration(Keyword=topic, MoA_Based_Optimization_Result_File=moa_based_optimization_result_file, Compression=compression, user_id=user_id, task=task)
    return {"result_file": result_file, "task_id": task.request["id"], "user_id": user_id}

