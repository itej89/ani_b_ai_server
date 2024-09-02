#!/bin/bash

# echo -ne "\033]0;fmService\007"

# source ~/anaconda3/etc/profile.d/conda.sh

# conda activate fmService

cd ./fmService

python3 manage.py runserver 10.104.60.111:8088