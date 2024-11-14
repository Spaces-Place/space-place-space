#!/bin/bash

# AWS 설정 생성
mkdir ~/.aws
echo "[default]" > ~/.aws/config
echo "region = ap-northeast-2" >> ~/.aws/config
echo "output = json" >> ~/.aws/config

# uvicorn 서버 시작
exec uvicorn main:app --host 0.0.0.0 --port 80