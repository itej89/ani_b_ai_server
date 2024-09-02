FROM nvidia/cuda:11.8.0-base-ubuntu20.04

ENV LD_LIBRARY_PATH /usr/lib/x86_64-linux-gnu/:$LD_LIBRARY_PATH

RUN apt-get update

RUN apt install ffmpeg -y

RUN apt-get install python3-pip  -y

RUN pip install --upgrade pip

RUN pip install -U openai-whisper

RUN pip install setuptools-rust

EXPOSE 3582

WORKDIR "/app/whisper"

ENTRYPOINT ["python3", "Server.py"]

