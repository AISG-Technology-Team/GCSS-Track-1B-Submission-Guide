#!/bin/bash

export ISOLATED_DOCKER_NETWORK_NAME=exec_env_jail_network
export GCSS_SERVER_CONTAINER_NAME=vllm_server
export GCSS_SERVER="http://${GCSS_SERVER_CONTAINER_NAME}"
export DOCKER_IMAGE_FOR_SAMPLE_SUBMISSION=sample_container


cat ../sample_io/test_stdin/stdin_local.json | \
docker run --init \
        --rm \
        --attach "stdin" \
        --attach "stdout" \
        --attach "stderr" \
        --cpus 2 \
        --gpus "device=1" \
        -e GCSS_SERVER="${GCSS_SERVER}" \
        -e NVIDIA_VISIBLE_DEVICES=1 \
        -e CUDA_VISIBLE_DEVICES=1 \
        --memory 4g \
        --memory-swap 0 \
        --ulimit nproc=1024 \
        --ulimit nofile=1024 \
        --network "${ISOLATED_DOCKER_NETWORK_NAME}" \
        --read-only \
        --mount type=tmpfs,destination=/tmp,tmpfs-size=5368709120,tmpfs-mode=1777 \
        --interactive \
        "${DOCKER_IMAGE_FOR_SAMPLE_SUBMISSION}" \
 1>../sample_io/test_output/stdout.json \
 2>../sample_io/test_output/stderr.log
