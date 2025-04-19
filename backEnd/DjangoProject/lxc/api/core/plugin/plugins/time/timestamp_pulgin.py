from datetime import datetime

import pytz

from api.core.plugin.plugins.base_plugin import BasePlugin


class TimestampPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="TimestampPlugin",
            version="1.0",
            description="获取时间戳",
            intent="Obtain_the_timestamp",
            param_description= {
                "timezone": "The timezone for which the current time is requested. "
                            "default: None. "
                            "Format: A string representing a timezone, e.g., \"Asia/Tokyo\", \"America/New_York\".",
                "readable_time": "A human-readable time that the timestamp is based on. "
                                 "default: None"
                                 "Format: A string in the format \"%Y-%m-%d %H:%M:%S\"."
            }
        )

    def execute(self, *args, **kwargs):
        # 从 kwargs 中获取时区信息、时间信息
        timezone = kwargs.get("timezone")
        readable_time = kwargs.get("readable_time")
        try:
            if timezone:
                tz = pytz.timezone(timezone)
            else:
                tz = datetime.now().astimezone().tzinfo

            if not readable_time:
                readable_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            timestamp = datetime.strptime(readable_time, "%Y-%m-%d %H:%M:%S").timestamp()

            timestamp_info = {
                "timestamp": timestamp
            }
            return {"status": "success", "result": timestamp_info}
        except pytz.UnknownTimeZoneError:
            return {"status": "error", "message": f"Unknown timezone: {timezone}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print(TimestampPlugin().execute(timezone="Asia/Tokyo", readable_time="2024-1-1 10:0:0"))