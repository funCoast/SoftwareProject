from datetime import datetime

import pytz

from api.core.plugin.plugins.base_plugin import BasePlugin


class TimePlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="TimePlugin",
            version="1.0",
            description="获取当前时间"
        )

    def execute(self, *args, **kwargs):
        # 从 kwargs 中获取时区信息
        timezone = kwargs.get("timezone")
        try:
            if timezone:
                tz = pytz.timezone(timezone)
            else:
                tz = datetime.now().astimezone().tzinfo

            current_time = datetime.now(tz)
            time_info = {
                "year": current_time.year,
                "month": current_time.month,
                "day": current_time.day,
                "hour": current_time.hour,
                "minute": current_time.minute,
                "second": current_time.second,
                "microsecond": current_time.microsecond,
                "timezone": str(tz),
                "isoformat": current_time.isoformat()
            }
            return {"status": "success", "result": time_info}
        except pytz.UnknownTimeZoneError:
            return {"status": "error", "message": f"Unknown timezone: {timezone}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print(TimePlugin().execute(timezone="Asia/Tokyo"))