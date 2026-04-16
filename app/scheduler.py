from __future__ import annotations

import argparse
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import get_settings
from app.orchestrator import ResearchAnalystApp


def run_loop(app: ResearchAnalystApp):
    eastern = ZoneInfo("US/Eastern")
    print("Scheduler running in US/Eastern. Press Ctrl+C to stop.")
    while True:
        now = datetime.now(tz=eastern)
        weekday = now.weekday()  # Mon=0

        # Pre-market run at 08:45 ET weekdays.
        if weekday < 5 and now.hour == 8 and now.minute == 45:
            app.run_once("pre_market")
            time.sleep(65)
            continue

        # Post-market run at 16:20 ET weekdays.
        if weekday < 5 and now.hour == 16 and now.minute == 20:
            app.run_once("post_market")
            time.sleep(65)
            continue

        # Weekend macro review Saturday 10:00 ET.
        if weekday == 5 and now.hour == 10 and now.minute == 0:
            app.run_once("weekend_macro")
            time.sleep(65)
            continue

        time.sleep(20)


def main():
    parser = argparse.ArgumentParser(description="AI hedge-fund style research analyst scheduler")
    parser.add_argument("--once", action="store_true", help="Run single daily scan and exit")
    args = parser.parse_args()

    settings = get_settings()
    app = ResearchAnalystApp(settings)

    if args.once:
        result = app.run_once("manual")
        print(f"Completed. Report => {result['report_path']}")
        return

    run_loop(app)


if __name__ == "__main__":
    main()
