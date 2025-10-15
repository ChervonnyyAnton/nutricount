"""Gunicorn configuration optimized for Raspberry Pi Zero 2W
Memory-optimized settings for 512MB RAM constraint"""

import os
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 128  # Reduced from 2048

# Worker processes - optimized for Pi Zero 2W
workers = 1  # Single worker to save memory
worker_class = "sync"
worker_connections = 50  # Reduced from 1000
timeout = 60  # Increased timeout for slower Pi
keepalive = 5  # Increased keepalive

# Restart workers after fewer requests to prevent memory leaks
max_requests = 200  # Reduced from 1000
max_requests_jitter = 20  # Reduced from 100

# Disable preload to save memory
preload_app = False

# Logging - minimal logging to save disk I/O
accesslog = "-"  # Log to stdout instead of file
errorlog = "-"   # Log to stderr instead of file
loglevel = "warning"  # Reduced logging level

# Process naming
proc_name = "nutrition_tracker_pi"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn_nutrition_pi.pid"
user = None
group = None
tmp_upload_dir = None

# Memory optimization settings
worker_tmp_dir = "/dev/shm"  # Use RAM for temporary files
max_requests_jitter = 20

# SSL (disabled for Pi Zero 2W to save resources)
keyfile = None
certfile = None

# Additional Pi Zero 2W optimizations
worker_class = "sync"  # Most memory efficient
worker_connections = 50  # Conservative connection limit
timeout = 60  # Longer timeout for slower processing
graceful_timeout = 30  # Graceful shutdown timeout
keepalive = 5  # Keep connections alive longer
