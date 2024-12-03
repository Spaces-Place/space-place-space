from dataclasses import dataclass
import os


@dataclass
class AWSCredentials:
    access_key: str
    secret_key: str
    region: str


class Credential:

    # 개발: 주입받기
    @staticmethod
    def get_credentials() -> AWSCredentials:
        import os

        if os.getenv("APP_ENV") == "development":
            return AWSCredentials(
                access_key=os.getenv("SPACE_ACCESS_KEY"),
                secret_key=os.getenv("SPACE_SECRET_KEY"),
                region=os.getenv("REGION_NAME"),
            )

        return Credential._get_production_credentials()

    # 운영: 파일에서 읽기
    @staticmethod
    def _get_production_credentials() -> AWSCredentials:
        try:
            with (
                open("/etc/secret-volume/access", "r") as access_file,
                open("/etc/secret-volume/secret", "r") as secret_file,
            ):
                return AWSCredentials(
                    access_key=access_file.read().strip(),
                    secret_key=secret_file.read().strip(),
                    region=os.getenv("REGION_NAME"),
                )

        except FileNotFoundError as e:
            raise RuntimeError(f"자격 증명 파일을 찾을 수 없습니다: {e}")
