from typing import Dict, Any, List

class SkillContract:
    """定义技能的输入/输出契约与元数据"""
    def __init__(self, name: str, description: str, inputs: Dict[str, str], outputs: Dict[str, str], level: int):
        self.name = name
        self.description = description
        self.inputs = inputs
        self.outputs = outputs
        self.level = level

def get_skill_registry() -> Dict[str, SkillContract]:
    """返回已注册技能的元数据与契约"""
    return {
        "initial_idea": SkillContract(
            name="initial_idea",
            description="Generate initial idea from facts and hypotheses.",
            inputs={"topic": "str", "num": "int", "compression": "bool", "user_id": "str"},
            outputs={"result_file": "str", "task_id": "str", "user_id": "str"},
            level=4,
        ),
        "technical_optimization": SkillContract(
            name="technical_optimization",
            description="Optimize the idea with technical details and related papers.",
            inputs={"topic": "str", "initial_idea_result_file": "str", "compression": "bool", "user_id": "str"},
            outputs={"result_file": "str", "task_id": "str", "user_id": "str"},
            level=4,
        ),
        "moa_based_optimization": SkillContract(
            name="moa_based_optimization",
            description="Run MoA-based optimization with multi-agent review.",
            inputs={"topic": "str", "technical_optimization_result_file": "str", "compression": "bool", "user_id": "str"},
            outputs={"result_file": "str", "task_id": "str", "user_id": "str"},
            level=4,
        ),
        "human_ai_collaboration": SkillContract(
            name="human_ai_collaboration",
            description="Perform human-AI collaboration to finalize optimization.",
            inputs={"topic": "str", "moa_based_optimization_result_file": "str", "compression": "bool", "user_id": "str"},
            outputs={"result_file": "str", "task_id": "str", "user_id": "str"},
            level=4,
        ),
    }

def make_default_plan(topic: str, num: int, compression: bool, user_id: str) -> List[Dict[str, Any]]:
    """生成默认的技能计划（线性执行链）"""
    return [
        {
            "skill": "initial_idea",
            "params": {"topic": topic, "num": num, "compression": compression, "user_id": user_id},
        },
        {
            "skill": "technical_optimization",
            "params": {"topic": topic, "compression": compression, "user_id": user_id, "initial_idea_result_file": None},
        },
        {
            "skill": "moa_based_optimization",
            "params": {"topic": topic, "compression": compression, "user_id": user_id, "technical_optimization_result_file": None},
        },
        {
            "skill": "human_ai_collaboration",
            "params": {"topic": topic, "compression": compression, "user_id": user_id, "moa_based_optimization_result_file": None},
        },
    ]

def orchestrate(plan: List[Dict[str, Any]]) -> Dict[str, Any]:
    """执行技能计划，按契约检验输入并串联上下文输出"""
    registry = get_skill_registry()
    context: Dict[str, Any] = {}
    for step in plan:
        skill = step.get("skill")
        params = step.get("params", {})
        if skill not in registry:
            raise ValueError(f"Unknown skill: {skill}")
        contract = registry[skill]
        # 补全依赖输入（从上下文获取）
        for key in contract.inputs.keys():
            if params.get(key) is None and key in context:
                params[key] = context[key]
        # 基础必需参数检查
        missing = [k for k in contract.inputs.keys() if params.get(k) is None]
        if missing:
            raise ValueError(f"Missing inputs for {skill}: {', '.join(missing)}")
        # 执行技能
        if skill == "initial_idea":
            from scispark_ms_skills.skills.initial_idea.scripts.main import run as run_initial
            result = run_initial(
                topic=params["topic"],
                search_paper_num=int(params["num"]),
                compression=bool(params["compression"]),
                user_id=params["user_id"],
            )
            # 将输出写入上下文以供后续技能使用
            context["initial_idea_result_file"] = result.get("result_file")
            # 记录首阶段生成的 task_id 与 user_id，供后续阶段复用
            if isinstance(result, dict):
                if result.get("task_id"):
                    context["task_id"] = result.get("task_id")
                if result.get("user_id"):
                    context["user_id"] = result.get("user_id")
        elif skill == "technical_optimization":
            from scispark_ms_skills.skills.technical_optimization.scripts.main import run as run_tech
            result = run_tech(
                topic=params["topic"],
                initial_idea_result_file=params["initial_idea_result_file"],
                compression=bool(params["compression"]),
                user_id=params["user_id"],
                task_id=context.get("task_id"),
            )
            context["technical_optimization_result_file"] = result.get("result_file")
        elif skill == "moa_based_optimization":
            from scispark_ms_skills.skills.moa_based_optimization.scripts.main import run as run_moa
            result = run_moa(
                topic=params["topic"],
                technical_optimization_result_file=params["technical_optimization_result_file"],
                compression=bool(params["compression"]),
                user_id=params["user_id"],
                task_id=context.get("task_id"),
            )
            context["moa_based_optimization_result_file"] = result.get("result_file")
        elif skill == "human_ai_collaboration":
            from scispark_ms_skills.skills.human_ai_collaboration.scripts.main import run as run_hac
            result = run_hac(
                topic=params["topic"],
                moa_based_optimization_result_file=params["moa_based_optimization_result_file"],
                compression=bool(params["compression"]),
                user_id=params["user_id"],
                task_id=context.get("task_id"),
            )
            # 最终阶段输出可直接加入上下文
        else:
            raise NotImplementedError(f"Skill not implemented: {skill}")
        # 合并输出（保留最近 task_id 与 user_id）
        if isinstance(result, dict):
            context.update(result)
    return context

