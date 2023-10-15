import multiprocessing
from psycogreen.gevent import patch_psycopg

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1

def post_fork(server, worker):
    patch_psycopg()
    worker.log.info("Made Psycopg2 Green")



    from django_db_geventpool.utils import close_connection

@close_connection
def foo_func()