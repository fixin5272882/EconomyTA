# clock.py
from apscheduler.schedulers.blocking import BlockingScheduler
import urllib.request

sched = BlockingScheduler()

#定時去搓url讓服務不中斷
@sched.scheduled_job('cron', day_of_week='mon-sun', minute='*/14')
def scheduled_job():
    url = "https://economyta-test.onrender.com"
    conn = urllib.request.urlopen(url)
    for key, value in conn.getheaders():
        print(key, value)
    print("戳一下")

sched.start()