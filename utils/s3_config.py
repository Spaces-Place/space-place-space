from typing import Dict
import boto3

from utils.aws_ssm_key import get_space_access_key, get_space_secret_key

def s3_bucket() -> Dict:
    SPACE_S3_ACCESS_KEY = get_space_access_key()
    SPACE_S3_SECRET_KEY = get_space_secret_key()
    BUCKET_NAME = 'space-place-bucket'

    print(SPACE_S3_ACCESS_KEY)
    print(SPACE_S3_SECRET_KEY)

    # S3 클라이언트 생성
    s3_client = boto3.client(
        's3',
        aws_s3_access_key_id=SPACE_S3_ACCESS_KEY,
        aws_s3_secret_access_key=SPACE_S3_SECRET_KEY
    )

    return {
        "s3_client": s3_client,
        "bucket": BUCKET_NAME
    }