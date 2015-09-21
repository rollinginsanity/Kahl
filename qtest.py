from redis import Redis
from rq import Queue
from addf import extractcomic
import time

redis_conn = Redis()
q = Queue(connection=redis_conn)  # no args implies the default queue

job = q.enqueue(extractcomic, 'comics/unprocessed/masseffect_foundation_vol1.cbz')

print(job.result)

time.sleep(2)

print(job.result) 
