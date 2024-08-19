import os

# Fixed - model_name_map - pre-downloaded
MODEL_IDX = {
    0: "meta-llama/Llama-2-7b-chat-hf",
}

# Environment Variables, TODO: Replace with pydantic-settings or dotenv?
TEST_RUN = os.getenv("TEST_RUN", False)
ATTACK_PROMPT_MAX_TOKEN_LENGTH = int(
    os.getenv("VLLM_RESPONSE_MAX_TOKEN_LENGTH", 256)
)
VLLM_RESPONSE_MAX_TOKEN_LENGTH = int(
    os.getenv("VLLM_RESPONSE_MAX_TOKEN_LENGTH", 256)
)
MODEL_FILES_LOCATION = os.getenv("MODEL_FILES_LOCATION", "./models")
