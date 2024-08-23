import os

# Environment Variables
GCSS_SERVER_CONTAINER_NAME = os.getenv(
    "GCSS_SERVER_CONTAINER_NAME", "vllm_server"
)
GCSS_SERVER = f"http://{GCSS_SERVER_CONTAINER_NAME}"
