"""
Scheduled Job Example
=====================
Run functions on a cron schedule.
Great for periodic tasks like data sync, cleanup, reports.

Deploy: beam deploy scheduled_job.py:hourly_report
"""

from beam import schedule, Image
import json


@schedule(
    name="hourly-metrics",
    when="0 * * * *",  # Every hour at minute 0
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11").add_python_packages([
        "requests",
    ]),
)
def hourly_report():
    """
    Runs every hour to collect and report metrics.
    
    Cron format: minute hour day month weekday
    Examples:
        "0 * * * *"     - Every hour
        "*/15 * * * *"  - Every 15 minutes
        "0 0 * * *"     - Daily at midnight
        "0 9 * * 1-5"   - Weekdays at 9 AM
        "0 0 1 * *"     - First of every month
    """
    from datetime import datetime
    
    timestamp = datetime.utcnow().isoformat()
    
    metrics = {
        "timestamp": timestamp,
        "type": "hourly_report",
        "data": {
            "active_users": 42,
            "requests_per_minute": 150,
            "error_rate": 0.02,
        },
    }
    
    print(f"Hourly report generated: {json.dumps(metrics)}")
    
    return metrics


@schedule(
    name="daily-cleanup",
    when="0 2 * * *",  # Daily at 2 AM UTC
    cpu=2,
    memory="1Gi",
    image=Image(python_version="python3.11"),
)
def daily_cleanup():
    """
    Daily cleanup job for maintenance tasks.
    """
    from datetime import datetime
    import time
    
    start = time.time()
    
    cleaned_items = 0
    for i in range(100):
        time.sleep(0.01)
        cleaned_items += 1
    
    elapsed = time.time() - start
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "items_cleaned": cleaned_items,
        "duration_seconds": round(elapsed, 2),
    }


@schedule(
    name="weekly-digest",
    when="0 9 * * 1",  # Every Monday at 9 AM UTC
    cpu=1,
    memory="1Gi",
    image=Image(python_version="python3.11").add_python_packages([
        "requests",
    ]),
)
def weekly_digest():
    """
    Weekly summary report.
    """
    from datetime import datetime, timedelta
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    return {
        "report_type": "weekly_digest",
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "summary": {
            "total_events": 1250,
            "unique_users": 340,
            "top_actions": ["login", "view", "purchase"],
        },
    }
