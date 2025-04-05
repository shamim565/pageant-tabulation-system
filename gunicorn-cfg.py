# Bind to Render's expected host and port
bind = "0.0.0.0:8000"  # Render requires port 10000

# Number of workers
workers = 1 

# Logging settings
accesslog = "-"  # Log to stdout, visible in Render dashboard
loglevel = "debug"  # Detailed logging for troubleshooting
capture_output = True  # Capture all output to logs
enable_stdio_inheritance = True  # Allow subprocesses to inherit stdio

# Additional recommended settings for stability
timeout = 30  # Restart workers if they hang for 30 seconds
max_requests = 1000  # Restart workers after 1000 requests to prevent leaks
max_requests_jitter = 50  # Add randomness to restarts
