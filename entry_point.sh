#!/bin/bash

# AWS 설정 디렉토리 생성 (권한 확인)
mkdir -p /root/.aws

# AWS 설정 파일 생성
cat > /root/.aws/config << EOF
[default]
region = ap-northeast-2
output = json
EOF

# 권한 설정
chmod 600 /root/.aws/config

# uvicorn 서버 시작
exec uvicorn main:app --host 0.0.0.0 --port 80