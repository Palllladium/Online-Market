import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from common.common.core.db_config import INTERVAL
from etl import run_etl


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_etl, "interval", seconds=INTERVAL)
    scheduler.start()

    print(f"[ETL] Scheduler started. Interval: {INTERVAL} seconds")

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())