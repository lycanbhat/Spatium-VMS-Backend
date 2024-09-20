import multiprocessing

# Define the address and port where Gunicorn will listen
bind = 'localhost:8000'

# Number of workers
workers = multiprocessing.cpu_count() * 2 + 1

# Specify the worker class
worker_class = 'gevent'

# Number of threads per worker
threads = 2

# Timeout for worker processes
timeout = 30

# Maximum number of requests a worker will process before restarting
max_requests = 1000

# Maximum number of requests a worker will process before restarting
max_requests_jitter = 50

# Worker graceful restart
graceful_timeout = 10

# Logging
accesslog = '-'  # '-' means log to stdout
errorlog = '-'   # '-' means log to stderr
loglevel = 'info'

wsgi_app='spatium.wsgi:application'

raw_env = ['DJANGO_SETTINGS_MODULE=spatium.settings']
