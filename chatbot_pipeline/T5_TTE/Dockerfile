ARG BASE=nvidia/cuda:11.8.0-base-ubuntu20.04
FROM ${BASE}

RUN apt-get update

RUN apt-get install -y python3-pip

RUN pip3 install torch transformers sentencepiece protobuf accelerate bitsandbytes scipy flask

EXPOSE 3579

ENTRYPOINT ["python3", "/app/tte/Server.py"]
