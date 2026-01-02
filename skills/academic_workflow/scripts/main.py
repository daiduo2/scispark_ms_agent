import uuid
from scispark_ms_skills.common.workflow import Initial_Idea, Technical_Optimization, MoA_Based_Optimization, Human_AI_Collaboration

class SimpleTask:
    def __init__(self, task_id=None):
        self.request = {"id": task_id or str(uuid.uuid4())}

def run(topic: str, search_paper_num: int = 5, compression: bool = True, user_id: str = "skill_user"):
    task = SimpleTask()
    initial_file = Initial_Idea(Keyword=topic, SearchPaperNum=search_paper_num, Compression=compression, user_id=user_id, task=task)
    tech_file = Technical_Optimization(Keyword=topic, Initial_Idea_Result_File=initial_file, Compression=compression, user_id=user_id, task=task)
    moa_file = MoA_Based_Optimization(Keyword=topic, Technical_Optimization_Result_File=tech_file, Compression=compression, user_id=user_id, task=task)
    final_file = Human_AI_Collaboration(Keyword=topic, MoA_Based_Optimization_Result_File=moa_file, Compression=compression, user_id=user_id, task=task)
    return {
        "initial": initial_file,
        "technical": tech_file,
        "moa": moa_file,
        "final": final_file,
        "task_id": task.request["id"],
        "user_id": user_id
    }

