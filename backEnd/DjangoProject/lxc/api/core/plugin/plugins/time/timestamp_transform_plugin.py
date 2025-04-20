from datetime import datetime

import pytz

from api.core.plugin.plugins.base_plugin import BasePlugin


class TimestampTransformPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="TimestampTransformPlugin",
            version="1.0",
            description="时间戳转换为时间",
            intent="Calculate_the_time_based_on_the_timestamp",
            param_description= {
                "timezone": "The timezone for which the current time is requested. "
                            "default: None. "
                            "Format: A string representing a timezone, e.g., \"Asia/Tokyo\", \"America/New_York\".",
                "timestamp": "The timestamp to be converted. "
                             "Format: A numeric value representing the timestamp."
            }
        )

    def execute(self, *args, **kwargs):
        # 从 kwargs 中获取时区信息、时间戳
        timezone = kwargs.get("timezone")
        timestamp = kwargs.get("timestamp")
        try:
            if timezone:
                tz = pytz.timezone(timezone)
            else:
                tz = datetime.now().astimezone().tzinfo

            utc_time = datetime.fromtimestamp(int(timestamp), tz)
            local_time = utc_time.astimezone(tz)

            timestamp_info = {
                "time_str": local_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            return {"status": "success", "result": timestamp_info}
        except pytz.UnknownTimeZoneError:
            return {"status": "error", "message": f"Unknown timezone: {timezone}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print(TimestampTransformPlugin().execute(timezone="Asia/Shanghai", timestamp="11"))