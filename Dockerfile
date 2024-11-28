FROM python:3.12.3-alpine3.20

# 필요한 시스템 패키지 설치
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    python3-dev \
    libffi-dev \
    openssl-dev \
    cargo

WORKDIR /code

# requirements 설치
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# entry_point.sh 복사 및 권한 설정
COPY ./entry_point.sh /code/entry_point.sh
RUN chmod +x /code/entry_point.sh

# 애플리케이션 코드 복사
COPY ./ ./

# 포트 설정
EXPOSE 80

# entry_point.sh 실행
CMD ["sh", "/code/entry_point.sh"]