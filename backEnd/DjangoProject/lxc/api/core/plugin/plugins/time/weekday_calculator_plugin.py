from datetime import datetime

from api.core.plugin.plugins.base_plugin import BasePlugin


class WeekdayCalculatorPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="WeekdayCalculatorPlugin",
            version="1.0",
            description="计算指定日期是星期几"
        )

    def execute(self, *args, **kwargs) -> dict:
        try:
            date = kwargs["date"]
            # 如果没有提供日期，默认使用当前日期
            if not date:
                date_obj = datetime.now()
            else:
                if isinstance(date, str):
                    date_obj = datetime.fromisoformat(date)
                elif isinstance(date, datetime):
                    date_obj = date
                else:
                    return {"status": "error",
                            "message": "Invalid date format. Please use ISO 8601 format (YYYY-MM-DD)."}

            # 获取星期几（
            weekday_index = date_obj.weekday()
            weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            weekday_name = weekdays[weekday_index]

            return {
                "status": "success",
                "result": {
                    "date": date_obj.isoformat(),
                    "weekday": weekday_name
                }
            }
        except ValueError as e:
            return {"status": "error", "message": f"Invalid date: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print(WeekdayCalculatorPlugin().execute(date="2025-04-11"))