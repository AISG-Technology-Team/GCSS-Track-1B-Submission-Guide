#!/bin/bash

# Define network name
export ISOLATED_DOCKER_NETWORK_NAME=exec_env_jail_network \
    ISOLATED_DOCKER_NETWORK_DRIVER=bridge \
    ISOLATED_DOCKER_NETWORK_INTERNAL=true \
    ISOLATED_DOCKER_NETWORK_SUBNET=172.50.0.0/16

# Run the VLLM FastAPI (with docker-compose.yml)
export DOCKER_IMAGE_FOR_VLLM=backend_server:latest
export GCSS_SERVER=vllm_server
# docker compose -f docker-compose.yml up --build --remove-orphans
docker compose -f docker-compose.yml up


# Run the VLLM FastAPI (with docker run ...)
# Create docker network
# docker network create \
#     --driver "$ISOLATED_DOCKER_NETWORK_DRIVER" \
#     $( [ "$ISOLATED_DOCKER_NETWORK_INTERNAL" = "true" ] && echo "--internal" ) \
#     --subnet "$ISOLATED_DOCKER_NETWORK_SUBNET" \
#     "$ISOLATED_DOCKER_NETWORK_NAME"

# Export Environment Variables
# export DOCKER_IMAGE_FOR_VLLM=backend_server:latest
# export GCSS_SERVER=vllm_server
# docker run --name "$GCSS_SERVER" \
# 	--rm \
#     --cpus 2 \
#     --runtime=nvidia \
#     --network "$ISOLATED_DOCKER_NETWORK_NAME" \
# 	--ip=172.50.0.2 \
# 	--expose 8000 \
# 	-p 8000:8000 \
# 	-e NVIDIA_VISIBLE_DEVICES=0 \
#     -e TEST_RUN=true \
#     -e ATTACK_PROMPT_MAX_TOKEN_LENGTH=256 \
#     -e VLLM_RESPONSE_MAX_TOKEN_LENGTH=256 \
#     -e MODEL_FILES_LOCATION=./models \
# 	-v models:/app/models \
# 	-v logs:/app/logs \
# 	"$DOCKER_IMAGE_FOR_VLLM" \
# 	uvicorn app:app --host 172.50.0.2 --port 8000
