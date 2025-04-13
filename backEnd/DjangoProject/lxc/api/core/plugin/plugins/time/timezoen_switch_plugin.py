from datetime import datetime

import pytz

from api.core.plugin.plugins.base_plugin import BasePlugin


class TimezoneSwitchPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="TimezoneSwitchPlugin",
            version="1.0",
            description="时区转换"
        )

    def execute(self, *args, **kwargs):
        try:
            # 获取输入参数
            input_time = kwargs.get("time")
            current_tz_name = kwargs.get("current_timezone", "UTC")
            target_tz_name = kwargs.get("target_timezone", "UTC")

            if isinstance(input_time, str):
                input_time = datetime.fromisoformat(input_time)
            elif not input_time:
                input_time = datetime.now()

            current_tz = pytz.timezone(current_tz_name)
            target_tz = pytz.timezone(target_tz_name)

            current_time = current_tz.localize(input_time)

            target_time = current_time.astimezone(target_tz)

            # 返回的时间信息
            time_info = {
                "year": target_time.year,
                "month": target_time.month,
                "day": target_time.day,
                "hour": target_time.hour,
                "minute": target_time.minute,
                "second": target_time.second,
                "microsecond": target_time.microsecond,
                "timezone": str(target_tz),
                "isoformat": target_time.strftime("%Y-%m-%d %H:%M:%S")
            }

            return {"status": "success", "result": time_info}

        except pytz.UnknownTimeZoneError as e:
            return {"status": "error", "message": f"Unknown timezone: {str(e)}"}
        except ValueError as e:
            return {"status": "error", "message": f"Invalid input time: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    print(TimezoneSwitchPlugin().execute(time="2024-10-15 14:30:45", current_timezone="Asia/Shanghai", target_timezone="Asia/Tokyo"))