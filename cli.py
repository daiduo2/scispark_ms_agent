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

if __name__ == "__main__":
    main()
