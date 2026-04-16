from __future__ import annotations

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import AppConfig
from app.research_system import ResearchSystem


def run_scheduler(config: AppConfig) -> None:
    system = ResearchSystem(config)
    scheduler = BlockingScheduler(timezone="UTC")

    scheduler.add_job(system.run_once, CronTrigger(day_of_week="mon-fri", hour=config.pre_market_hour_utc, minute=0))
    scheduler.add_job(system.run_once, CronTrigger(day_of_week="mon-fri", hour=config.post_market_hour_utc, minute=15))

    print(
        f"Scheduler started (UTC). Pre-market at {config.pre_market_hour_utc}:00 and "
        f"post-market at {config.post_market_hour_utc}:15"
    )
    scheduler.start()


def main() -> None:
    run_scheduler(AppConfig.from_env())


if __name__ == "__main__":
    main()
