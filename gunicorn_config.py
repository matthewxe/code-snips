import os

workers = int(os.environ.get('GUNICORN_PROCESSES', '2'))
threads = int(os.environ.get('GUNICORN_THREADS', '4'))
# workers = int(os.environ.get('GUNICORN_PROCESSES', '2'))
# workers = int(os.environ.get('GUNICORN_WORKERS', '5'))
# threads = int(os.environ.get('GUNICORN_THREADS', '2'))
# os.environ.get('GUNICORN_WORKER_CLASS', 'gevent')
# os.environ.get('GUNICORN_WORKER_CONNECTIONS', '1000')

bind = os.environ.get('GUNICORN_BIND', 'localhost:8000')
forwarded_allow_ips = '*'
secure_scheme_headers = {'X-Forwarded-Proto': 'https'}
