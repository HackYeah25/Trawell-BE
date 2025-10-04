from celery import current_app as celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task
def example_task():
    """Example background task."""
    logger.info("Example task executed")
    return "Task completed successfully"

@celery_app.task
def process_travel_recommendation(data):
    """Process travel recommendation in background."""
    logger.info(f"Processing travel recommendation: {data}")
    # Add your travel recommendation processing logic here
    return {"status": "processed", "data": data}
