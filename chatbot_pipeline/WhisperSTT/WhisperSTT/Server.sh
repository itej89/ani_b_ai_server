#! /bin/bash


pwd=$(pwd)
export FM_AI_SERVICE_STT_PATH=${pwd}

source activate whisper

cd /app/WhisperSTT

python Server.py