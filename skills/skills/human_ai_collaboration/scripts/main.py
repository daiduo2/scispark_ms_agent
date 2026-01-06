import uuid
from common.workflow import Human_AI_Collaboration

class SimpleTask:
    def __init__(self, task_id=None):
        self.request = {"id": task_id or str(uuid.uuid4())}

def run(topic: str, moa_based_optimization_result_file: str, compression: bool = True, user_id: str = "skill_user", task_id: str = None):
    """执行人机协作阶段
    
    参数:
    - topic: 科研主题
    - moa_based_optimization_result_file: MoA 优化阶段的结果文件路径
    - compression: 是否对相关论文进行内容压缩
    - user_id: 用户标识，用于输出目录分隔
    - task_id: 任务标识，若提供则复用同一任务目录
    
    返回:
    - dict: 包含 result_file、task_id、user_id
    """
    task = SimpleTask(task_id=task_id)
    result_file = Human_AI_Collaboration(Keyword=topic, MoA_Based_Optimization_Result_File=moa_based_optimization_result_file, Compression=compression, user_id=user_id, task=task)
    return {"result_file": result_file, "task_id": task.request["id"], "user_id": user_id}
