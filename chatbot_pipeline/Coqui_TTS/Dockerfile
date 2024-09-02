ARG BASE=nvidia/cuda:11.8.0-base-ubuntu20.04
FROM ${BASE}
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends gcc g++ make python3 python3-dev python3-pip python3-venv python3-wheel espeak-ng libsndfile1-dev && rm -rf /var/lib/apt/lists/*
RUN pip3 install tts

EXPOSE 3578

WORKDIR "/app/tts"

ENTRYPOINT ["python3", "Server.py"]
