import os
import json
import time
import uuid
from typing import Dict, Any

PKG_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QUEUE_DB = os.path.join(PKG_DIR, "tasks.json")

def _load_tasks():
    if os.path.exists(QUEUE_DB):
        try:
            with open(QUEUE_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_tasks(tasks: Dict[str, Any]):
    tmp = QUEUE_DB + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    os.replace(tmp, QUEUE_DB)

def enqueue(topic: str, search_paper_num: int = 5, compression: bool = True, user_id: str = "skill_user") -> str:
    tasks = _load_tasks()
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "id": task_id,
        "topic": topic,
        "search_paper_num": search_paper_num,
        "compression": compression,
        "user_id": user_id,
        "status": "queued",
        "created_at": time.time(),
        "updated_at": time.time()
    }
    _save_tasks(tasks)
    return task_id

def process_once(interval: int = 0):
    tasks = _load_tasks()
    running = [t for t in tasks.values() if t.get("status") == "running"]
    if running:
        time.sleep(interval)
        return
    queued = [t for t in tasks.values() if t.get("status") == "queued"]
    if not queued:
        time.sleep(interval)
        return
    task = sorted(queued, key=lambda x: x.get("created_at", 0))[0]
    task_id = task["id"]
    tasks[task_id]["status"] = "running"
    tasks[task_id]["updated_at"] = time.time()
    _save_tasks(tasks)
    try:
        from scispark_ms_skills.skills.academic_workflow.scripts.main import run as run_workflow
        result = run_workflow(
            topic=task["topic"],
            search_paper_num=int(task.get("search_paper_num", 5)),
            compression=bool(task.get("compression", True)),
            user_id=task.get("user_id", "skill_user")
        )
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = result
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
    finally:
        tasks[task_id]["updated_at"] = time.time()
        _save_tasks(tasks)

def run_worker(interval: int = 3, once: bool = False):
    if once:
        process_once(interval)
        return
    while True:
        process_once(interval)
        time.sleep(interval)
