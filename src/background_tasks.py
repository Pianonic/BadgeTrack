import asyncio
import time
import logging
from .rate_limiter import cleanup_old_records

logger = logging.getLogger(__name__)

async def periodic_cleanup():
    while True:
        try:
            await asyncio.sleep(3600)
            cleanup_old_records()
            logger.info(f"Periodic cleanup completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        except asyncio.CancelledError:
            logger.info("Periodic cleanup task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {e}")

async def startup_tasks():
    try:
        cleanup_old_records()
        logger.info("Initial cleanup completed")
        cleanup_task = asyncio.create_task(periodic_cleanup())
        return cleanup_task
    except Exception as e:
        logger.error(f"Error in startup tasks: {e}")
        return None

async def shutdown_tasks(cleanup_task):
    try:
        if cleanup_task and not cleanup_task.done():
            cleanup_task.cancel()
            try:
                await cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Background tasks shutdown completed")
    except Exception as e:
        logger.error(f"Error in shutdown tasks: {e}")
