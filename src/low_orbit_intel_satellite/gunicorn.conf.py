from gevent import monkey
monkey.patch_all()

import multiprocessing
from psycogreen.gevent import patch_psycopg
from django_db_geventpool.utils import close_connection

bind = "0.0.0.0:8888"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
threads = 10
keep_alive=5
limit_request_fields=10000
user=69
group=69

timeout=300
graceful_timeout=120

max_requests=1500

wsgi_app='low_orbit_intel_satellite.wsgi'

def post_fork(server, worker):
    patch_psycopg()
    monkey.patch_all()
    worker.log.info("Monkey Patched Thread 🙊")


@close_connection
def foo_func():
    pass
