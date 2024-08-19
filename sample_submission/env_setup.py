import os

# Environment Variables
GCSS_SERVER = os.getenv("GCSS_SERVER", "localhost")
URL = f"http://{GCSS_SERVER}:8000"
