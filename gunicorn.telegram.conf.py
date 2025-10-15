import os
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes optimized for Telegram Web App traffic
workers = min(4, multiprocessing.cpu_count())
worker_class = "sync"
worker_connections = 1000
timeout = 60  # Longer timeout for Telegram webhooks
keepalive = 2

# Request handling
max_requests = 2000
max_requests_jitter = 200
preload_app = True

# Telegram-specific optimizations
worker_tmp_dir = "/dev/shm"  # Use RAM for temporary files

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s telegram_user=%({HTTP_X_TELEGRAM_USER}i)s'

# Process naming
proc_name = "nutrition_tracker_telegram"

# Server mechanics
daemon = False
pidfile = "/tmp/nutrition_tracker_telegram.pid"
user = None
group = None
tmp_upload_dir = None

# Security optimizations for Telegram
limit_request_line = 8192  # Larger for Telegram data
limit_request_fields = 200
limit_request_field_size = 16384

# Telegram webhook specific settings
forwarded_allow_ips = '*'  # Trust all proxies for Telegram webhooks
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
