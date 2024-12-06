import logging
import logging.config
from pathlib import Path
from datetime import datetime


class Logger:
    logger = None

    @staticmethod
    def setup_logger():
        service_name = "space"
        if Logger.logger is None:
            base_log_dir = Path(f"/var/log/spaceplace/{service_name}")
            base_log_dir.mkdir(parents=True, exist_ok=True)

            today = datetime.now().strftime("%Y%m%d")
            daily_log_dir = base_log_dir / today
            daily_log_dir.mkdir(exist_ok=True)

            log_config = {
                "version": 1,
                "formatters": {
                    "detailed": {
                        "format": "[%(asctime)s.%(msecs)03d] %(levelname)s [%(thread)d] - %(message)s",
                        "datefmt": "%Y-%m-%d %H:%M:%S",
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "level": "INFO",
                        "formatter": "detailed",
                    },
                    "file": {
                        "class": "logging.handlers.RotatingFileHandler",
                        "level": "INFO",
                        "formatter": "detailed",
                        "filename": str(daily_log_dir / "logfile.log"),
                        "maxBytes": 1024 * 1024,  # 1mb
                        "backupCount": 10,
                        "encoding": "utf-8",
                    },
                },
                "root": {"level": "INFO", "handlers": ["console", "file"]},
            }

            logging.config.dictConfig(log_config)
            Logger.logger = logging.getLogger()

        return Logger.logger
