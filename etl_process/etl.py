from datetime import datetime as dt, timezone

from extractor import extract_updated_products
from loader import load_to_elasticsearch
from common.common.core.db_config import get_db_session_instance


last_sync_time = dt.now(timezone.utc)


async def run_etl():
    global last_sync_time
    session = await get_db_session_instance()
    try:
        products = await extract_updated_products(session, last_sync_time)
        if products:
            await load_to_elasticsearch(products)
            print(f"[ETL] Synced {len(products)} updated product(s)")
        else:
            print("[ETL] No changes to sync.")
        last_sync_time = dt.now(timezone.utc)
    finally:
        await session.close()