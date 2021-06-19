from celery.schedules import crontab

TASKS = {
    'update_feed_task': {
        'task': 'update_feed_task',
        'schedule': crontab(minute='*/15'),  # update the feeds every 15 minutes
    },
}
