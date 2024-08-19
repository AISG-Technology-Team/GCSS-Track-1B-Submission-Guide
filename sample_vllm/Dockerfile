# FROM python:3.10-slim-bullseye
FROM nvidia/cuda:12.2.2-base-ubuntu22.04

###################### LAYER 1: Install dependencies ###########################
RUN apt-get update && \
    apt-get install python3.10 python3.10-venv -yqq

############ Copy required project files, source codes, etc ###########
#------ Implementation Specific - Engine related modules, etc --------#
RUN mkdir -p /app

# Given that the docker-compose "context" is .
COPY . /app

EXPOSE 8000

# Add venv/bin/activate to PATH to ensure /opt/venv is used within a RUN/CMD/ENTRYPOINT
# command. This also ensures any sub-process launched via main python script is
# launched within the specified venv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
RUN pip install --upgrade pip \ 
    && pip install -r requirements.txt

# #################### RUN script (server or client) ####################
# ENTRYPOINT/COMMAND RAN IN `docker run` and/or `docker-compose`

