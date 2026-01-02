import argparse
import json

def parse_bool(x):
    return str(x).lower() in {"1", "true", "yes", "y"}

def main():
    p = argparse.ArgumentParser(prog="scispark_ms_skills")
    sub = p.add_subparsers(dest="cmd", required=True)

    pw = sub.add_parser("workflow")
    pw.add_argument("--topic", required=True)
    pw.add_argument("--num", type=int, default=5)
    pw.add_argument("--compression", type=parse_bool, default=True)
    pw.add_argument("--user-id", default="cli_user")

    pe = sub.add_parser("enqueue")
    pe.add_argument("--topic", required=True)
    pe.add_argument("--num", type=int, default=5)
    pe.add_argument("--compression", type=parse_bool, default=True)
    pe.add_argument("--user-id", default="cli_user")

    pr = sub.add_parser("worker")
    pr.add_argument("--interval", type=int, default=3)
    pr.add_argument("--once", action="store_true")

    ps = sub.add_parser("status")
    ps.add_argument("--task-id", required=True)

    pl = sub.add_parser("list")
    pl.add_argument("--status")

    pc = sub.add_parser("cancel")
    pc.add_argument("--task-id", required=True)

    pn = sub.add_parser("continue")
    pn.add_argument("--task-id", required=True)

    pnl = sub.add_parser("nl")
    pnl.add_argument("--query", required=True)

    args = p.parse_args()

    if args.cmd == "workflow":
        from scispark_ms_skills.skills.academic_workflow.scripts.main import run as run_workflow
        result = run_workflow(topic=args.topic, search_paper_num=args.num, compression=args.compression, user_id=args.user_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cmd == "enqueue":
        from scispark_ms_skills.skills.academic_workflow.scripts.queue import enqueue
        tid = enqueue(topic=args.topic, search_paper_num=args.num, compression=args.compression, user_id=args.user_id)
        print(tid)
        return

    if args.cmd == "worker":
        from scispark_ms_skills.skills.academic_workflow.scripts.queue import run_worker
        run_worker(interval=args.interval, once=args.once)
        return

    if args.cmd == "status":
        from scispark_ms_skills.skills.academic_workflow.scripts.queue import get_task
        task = get_task(task_id=args.task_id)
        print(json.dumps(task, ensure_ascii=False, indent=2))
        return

    if args.cmd == "list":
        from scispark_ms_skills.skills.academic_workflow.scripts.queue import list_tasks
        tasks = list_tasks(status=args.status)
        print(json.dumps(tasks, ensure_ascii=False, indent=2))
        return

    if args.cmd == "cancel":
        from scispark_ms_skills.skills.academic_workflow.scripts.queue import cancel_task
        ok = cancel_task(task_id=args.task_id)
        print("true" if ok else "false")
        return

    if args.cmd == "continue":
        from scispark_ms_skills.skills.academic_workflow.scripts.queue import continue_task
        ok = continue_task(task_id=args.task_id)
        print("true" if ok else "false")
        return

    if args.cmd == "nl":
        from scispark_ms_skills.common.utils.llm_api import call_with_deepseek_jsonout
        system_prompt = (
            "You will parse the user's natural language into a JSON object with fields: "
            "intent (one of: start_workflow, enqueue_task, run_worker_once, run_worker, "
            "query_task_status, list_tasks, cancel_task, continue_task) and params (object)."
        )
        parsed = call_with_deepseek_jsonout(system_prompt=system_prompt, question=args.query)
        intent = (parsed or {}).get("intent")
        params = (parsed or {}).get("params", {})
        if intent == "start_workflow":
            topic = params.get("topic")
            num = int(params.get("num", 5))
            compression = parse_bool(params.get("compression", True))
            user_id = params.get("user_id", "cli_user")
            from scispark_ms_skills.skills.academic_workflow.scripts.main import run as run_workflow
            result = run_workflow(topic=topic, search_paper_num=num, compression=compression, user_id=user_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
        if intent == "enqueue_task":
            topic = params.get("topic")
            num = int(params.get("num", 5))
            compression = parse_bool(params.get("compression", True))
            user_id = params.get("user_id", "cli_user")
            from scispark_ms_skills.skills.academic_workflow.scripts.queue import enqueue
            tid = enqueue(topic=topic, search_paper_num=num, compression=compression, user_id=user_id)
            print(tid)
            return
        if intent == "run_worker_once":
            interval = int(params.get("interval", 3))
            from scispark_ms_skills.skills.academic_workflow.scripts.queue import run_worker
            run_worker(interval=interval, once=True)
            return
        if intent == "run_worker":
            interval = int(params.get("interval", 3))
            from scispark_ms_skills.skills.academic_workflow.scripts.queue import run_worker
            run_worker(interval=interval, once=False)
            return
        if intent == "query_task_status":
            task_id = params.get("task_id")
            from scispark_ms_skills.skills.academic_workflow.scripts.queue import get_task
            task = get_task(task_id=task_id)
            print(json.dumps(task, ensure_ascii=False, indent=2))
            return
        if intent == "list_tasks":
            status = params.get("status")
            from scispark_ms_skills.skills.academic_workflow.scripts.queue import list_tasks
            tasks = list_tasks(status=status)
            print(json.dumps(tasks, ensure_ascii=False, indent=2))
            return
        if intent == "cancel_task":
            task_id = params.get("task_id")
            from scispark_ms_skills.skills.academic_workflow.scripts.queue import cancel_task
            ok = cancel_task(task_id=task_id)
            print("true" if ok else "false")
            return
        if intent == "continue_task":
            task_id = params.get("task_id")
            from scispark_ms_skills.skills.academic_workflow.scripts.queue import continue_task
            ok = continue_task(task_id=task_id)
            print("true" if ok else "false")
            return

if __name__ == "__main__":
    main()
