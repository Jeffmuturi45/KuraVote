# gunicorn.conf.py
import os
import multiprocessing

# Number of workers (Render free tier has 2 cores)
workers = 2
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2

# Memory optimization
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Bind to port from environment
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
