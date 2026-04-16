from __future__ import annotations

import argparse

from app.config import AppConfig
from app.research_system import ResearchSystem
from app.scheduler import run_scheduler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI-powered stock research analyst")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("run-once", help="Generate a single daily briefing now")
    sub.add_parser("scheduler", help="Run automated pre/post market scheduler")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = AppConfig.from_env()

    if args.command == "run-once":
        ResearchSystem(config).run_once()
    elif args.command == "scheduler":
        run_scheduler(config)


if __name__ == "__main__":
    main()
