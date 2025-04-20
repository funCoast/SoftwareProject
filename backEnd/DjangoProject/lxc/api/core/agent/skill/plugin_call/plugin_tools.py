

current_time_tool = {
    "type": "function",
    "function": {
        "name": "CurrentTimePlugin",
        "description": "获取当前时间，支持指定时区。",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "时区名称（如 'Asia/Shanghai', 'America/New_York'）",
                    "default": "Asia/Shanghai"
                },
                "time_format": {
                    "type": "string",
                    "description": "时间格式（如 '%Y-%m-%d %H:%M:%S'）",
                    "default": "%Y-%m-%d %H:%M:%S"
                }
            },
            "required": []
        }
    }
}

weather_scraper_tool = {
    "type": "function",
    "function": {
        "name": "WeatherScraperPlugin",
        "description": "查询指定城市天气信息。",
        "parameters": {
            "type": "object",
            "properties": {
                "city_code": {
                    "type": "string",
                    "description": "Beijing",
                    "default": "Beijing",
                }
            },
            "required": ["city_code"]
        }
    }
}

timestamp_tool = {
    "type": "function",
    "function": {
        "name": "TimestampPlugin",
        "description": "获取时间戳，支持基于指定时间或当前时间。",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "时区名称（如 'Asia/Shanghai'）",
                    "default": "Asia/Shanghai"
                },
                "readable_time": {
                    "type": "string",
                    "description": "可读时间（如 '2023-10-10 14:30:00'）",
                    "default": "2023-10-10 14:30:00"
                }
            },
            "required": []
        }
    }
}

timestamp_transform_tool = {
    "type": "function",
    "function": {
        "name": "TimestampTransformPlugin",
        "description": "将时间戳转换为可读时间。",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "目标时区名称（如 'Asia/Shanghai'）",
                    "default": "Asia/Shanghai"
                },
                "timestamp": {
                    "type": "number",
                    "description": "待转换的时间戳",
                    "default": "114514"
                }
            },
            "required": ["timestamp"]
        }
    }
}

timezone_switch_tool = {
    "type": "function",
    "function": {
        "name": "TimezoneSwitchPlugin",
        "description": "在时区之间转换时间。",
        "parameters": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "string",
                    "description": "原始时间（如 '2023-10-10 14:30:00'）",
                    "default": "2023-10-10 14:30:00"
                },
                "current_timezone": {
                    "type": "string",
                    "description": "原始时区名称（如 'Asia/Shanghai'）",
                    "default": "Asia/Shanghai"
                },
                "target_timezone": {
                    "type": "string",
                    "description": "目标时区名称（如 'America/New_York'）",
                    "default": "Asia/Shanghai"
                }
            },
            "required": ["time", "current_timezone", "target_timezone"]
        }
    }
}

weekday_calculator_tool = {
    "type": "function",
    "function": {
        "name": "WeekdayCalculatorPlugin",
        "description": "计算指定日期是星期几。",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "日期（如 '2023-10-10'）"
                }
            },
            "required": ["date"]
        }
    }
}

tools = {
    "Calculate_the_time_based_on_the_timestamp": timestamp_transform_tool,
    "Query_the_current_time_of_given_timezone": current_time_tool,
    "Check_the_weather_according_to_the_city": weather_scraper_tool,
    "Obtain_the_timestamp": timestamp_tool,
    "Converts_time_from_one_timezone_to_another": timezone_switch_tool,
    "Calculates_and_returns_the_day_of_the_week_for_a_specified_date": weekday_calculator_tool
}
