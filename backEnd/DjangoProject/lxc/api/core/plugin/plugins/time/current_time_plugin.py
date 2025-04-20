from datetime import datetime

import pytz

from api.core.plugin.plugins.base_plugin import BasePlugin


class CurrentTimePlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="CurrentTimePlugin",
            version="1.0",
            description="获取当前时间",
            intent="Query_the_current_time_of_given_timezone",
            param_description= {
                "timezone": "The timezone for which the current time is requested. "
                            "default: None. "
                            "Format: A string representing a timezone, e.g., \"Asia/Tokyo\", \"America/New_York\".",
                "time_format": "The format in which the time should be returned. "
                               "default: \"%Y-%m-%d %H:%M:%S\"."
            }
        )

    def execute(self, *args, **kwargs):
        # 从 kwargs 中获取时区信息
        timezone = kwargs.get("timezone")
        time_format = kwargs.get("time_format")
        try:
            if timezone:
                tz = pytz.timezone(timezone)
            else:
                tz = datetime.now().astimezone().tzinfo

            if not time_format:
                time_format = "%Y-%m-%d %H:%M:%S"

            current_time = datetime.now(tz)
            result = {
                "year": current_time.year,
                "month": current_time.month,
                "day": current_time.day,
                "hour": current_time.hour,
                "minute": current_time.minute,
                "second": current_time.second,
                "microsecond": current_time.microsecond,
                "timezone": str(tz),
                "isoformat": current_time.strftime(time_format)
            }
            return {"status": "success", "result": result}
        except pytz.UnknownTimeZoneError:
            return {"status": "error", "message": f"Unknown timezone: {timezone}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print(CurrentTimePlugin().execute(timezone="Asia/Tokyo", time_format="%Y-%m-%d %H:%M"))