"""Gunicorn configuration optimized for Raspberry Pi 4 Model B 2018
Conservative settings for early revision with potential thermal issues"""

import os
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 256  # Conservative backlog for Pi 4 Model B 2018

# Worker processes - conservative for Pi 4 Model B 2018
workers = 1  # Single worker to avoid thermal issues
worker_class = "sync"
worker_connections = 75  # Conservative connections
timeout = 45  # Longer timeout for potential thermal throttling
keepalive = 8  # Moderate keepalive

# Restart workers more frequently to prevent thermal buildup
max_requests = 300  # Conservative for Pi 4 Model B 2018
max_requests_jitter = 30  # Conservative jitter

# Enable preload for better performance
preload_app = True

# Logging - detailed logging for troubleshooting
accesslog = "-"  # Log to stdout instead of file
errorlog = "-"   # Log to stderr instead of file
loglevel = "info"  # Detailed logging for Pi 4 Model B 2018

# Process naming
proc_name = "nutrition_tracker_pi4_2018"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn_nutrition_pi4_2018.pid"
user = None
group = None
tmp_upload_dir = None

# Memory optimization settings
worker_tmp_dir = "/dev/shm"  # Use RAM for temporary files
max_requests_jitter = 30

# SSL (disabled for local network)
keyfile = None
certfile = None

# Additional Pi 4 Model B 2018 optimizations
worker_class = "sync"  # Most memory efficient
worker_connections = 75  # Conservative connection limit
timeout = 45  # Longer timeout for potential throttling
graceful_timeout = 20  # Graceful shutdown timeout
keepalive = 8  # Moderate keepalive
