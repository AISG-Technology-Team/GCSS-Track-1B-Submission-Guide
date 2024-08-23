from huggingface_hub import snapshot_download
from huggingface_hub import login

login()

# Download models
snapshot_download(
    repo_id="meta-llama/Llama-2-7b-chat-hf",
    local_dir="models/meta-llama/Llama-2-7b-chat-hf",
    local_dir_use_symlinks=False,
)
