from fastapi import FastAPI, HTTPException, Request
from models import torch, Message, TokenLengthRequest, ChatRequest, load_models
from transformers import AutoTokenizer
from env_setup import *

import logging.config
import yaml
import time
from conversation import *

# Setup Logger for VLLM BE
# Load the logging config file
with open("./logging.yaml", "rt") as f:
    config = yaml.safe_load(f.read())

# Configure the logging module with the config file
logging.config.dictConfig(config)
logger = logging.getLogger("development")


# Start App()
app = FastAPI()


@app.on_event("startup")
async def startup_event():

    # Check for GPU availability and names
    logger.info(f"Number of GPUs available: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        logger.info(f"GPU {i}: {torch.cuda.get_device_name(i)}")

    global models
    models = load_models()
    logger.info(f"Application started successfully")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Request: {request.method} {request.url}")

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} completed in {process_time:.4f} seconds with status code {response.status_code}"
    )
    return response


@app.get("/")
async def read_root():
    logger.info("Root endpoint called")
    return {"message": "Hello!"}


@app.post("/attack_prompt/token_length")
async def attack_prompt_token_length(request: TokenLengthRequest):

    # use_fast=False here for Llama
    tokenizer = AutoTokenizer.from_pretrained(
        os.path.join(MODEL_FILES_LOCATION, "meta-llama/Llama-2-7b-chat-hf"),
        padding_side="left",
        use_fast=False,
    )
    tokenizer.pad_token = tokenizer.eos_token

    larger = False

    # tokenize the string and measure the size
    input_ids = tokenizer(request.prompt, padding=True, return_tensors="pt")
    input_ids_size = input_ids["input_ids"].size()
    input_ids_token = input_ids["input_ids"]

    if input_ids_size[1] > ATTACK_PROMPT_MAX_TOKEN_LENGTH:
        larger = True
        logger.info(
            f"PROMPT:{request.prompt}\tToken length:{input_ids_size[1]}\tRequest is unsuccessful."
        )
    else:
        logger.info(
            f"PROMPT:{request.prompt}\tToken length:{input_ids_size[1]}\tRequest is successful."
        )

    # Clear cache, etc before going to do actual run
    del tokenizer

    return {
        "response": {"success": not larger, "token_length": input_ids_size[1]}
    }


def conversation_template(request: ChatRequest):
    model_name = MODEL_IDX[request.model]

    conv = get_conv_template(model_name)

    while request.messages:
        msg = request.messages.pop()
        role = msg.role
        content = msg.content
        if role.strip().lower() == "system":
            conv.set_system_message(content)
        elif role.strip().lower() == "user":
            conv.append_message(conv.roles[0], content)
        elif role.strip().lower() == "assistant":
            conv.append_message(conv.roles[1], content)
        else:
            raise ValueError(f"{role} is not a valid role.")
    conv.append_message(conv.roles[1], None)
    full_convo = conv.get_prompt()
    return full_convo


@app.post("/chat/complete")
async def chat_complete(
    request: ChatRequest,
):

    # Get the model id (model:int) from request and get the tokenizer
    tokenizer = models[request.model]["tokenizer"]
    tokenizer.pad_token = tokenizer.eos_token

    # Load attack_prompt into the appropriate template manually (not using fastchat)
    model_name = MODEL_IDX[request.model]
    model = models[request.model]["model"]

    # Get the conversation from the request to send to the model
    current_test_case = conversation_template(request)

    # Tokenize the prompt
    input_ids = tokenizer(current_test_case, padding=True, return_tensors="pt")
    input_ids["input_ids"] = input_ids["input_ids"].cuda()
    input_ids["attention_mask"] = input_ids["attention_mask"].cuda()
    num_input_tokens = input_ids["input_ids"].shape[1]
    try:

        # generate output
        outputs = model.generate(
            input_ids["input_ids"],
            attention_mask=input_ids["attention_mask"].half(),
            max_new_tokens=VLLM_RESPONSE_MAX_TOKEN_LENGTH,
            pad_token_id=tokenizer.pad_token_id,
        )

        # truncate output (limit 256 token length) & decode back to string representation
        response = tokenizer.batch_decode(
            # outputs[:, num_input_tokens:max_response_tokens_to_judge],
            outputs[:, num_input_tokens:],
            skip_special_tokens=True,
        )

        logger.debug(
            f"VLLM:{request.model}\tATTACK PROMPT:{current_test_case}\tSTATUS CODE:200\tRESPONSE:{response[0]}"
        )

        return {
            "response": {
                "success": True,
                "message": {"role": "assistant", "content": response[0]},
            }
        }

    except Exception as e:
        status_code = 500
        logger.error(
            f"VLLM:{request.model}\tATTACK PROMPT:{current_test_case}\tSTATUS CODE:{status_code}\tRESPONSE: Error generating output"
        )
        return {
            "response": {
                "success": False,
                "message": {"role": "assistant", "content": e},
            }
        }
