from pydantic import BaseModel
from typing import List
from env_setup import *
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os


# Pydantic Models for FastAPI APIs
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: int
    messages: List[Message]


class TokenLengthRequest(BaseModel):
    prompt: str


# Loading VLLM Models
def load_model(model_idx: int = 0):
    """
    Return
    - tuple (Model, Tokenizer)
    """

    # preload model
    model_name_or_path = os.path.join(
        MODEL_FILES_LOCATION, MODEL_IDX[model_idx]
    )

    # get the model from model_name_or_path
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        torch_dtype=torch.float16,
        device_map="balanced",  # "auto"
    ).eval()

    # Setup tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_name_or_path,
        padding_side="left",
        use_fast=False,
    )

    return model, tokenizer


def load_models(test_run=TEST_RUN):
    """
    Return
    - models: dict("model": Model, "tokenizer: Tokenizer)
    """
    models = {}

    if test_run:
        model_idx = [0]  # run llama
    else:
        model_idx = list(MODEL_IDX.keys())

    for idx in model_idx:
        model, tokenizer = load_model(idx)
        models[idx] = {"model": model, "tokenizer": tokenizer}

    return models
