import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

from api.core.plugin.plugins.base_plugin import BasePlugin


class WeatherScraperPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="WeatherScraperPlugin",
            version="1.0",
            description="得到天气",
            intent="Check_the_weather_according_to_the_city",
            param_description={
                "city": "the city for which weather information is requested."
                        "default: None"
            }
        )


    def execute(self, *args, **kwargs):
        try:
            city_code = kwargs['city_code']
            # 设置Selenium WebDriver
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")  # 无头模式
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            # 构建请求URL
            url = f"https://www.weather.com.cn/weather/{city_code}.shtml"
            driver.get(url)
            # 等待页面加载完成
            time.sleep(3)
            # 获取页面源码
            page_source = driver.page_source
            driver.quit()

            # 解析HTML内容
            soup = BeautifulSoup(page_source, "html.parser")

            try:
                # 找到包含7天天气信息的 ul 标签
                weather_list = soup.find("ul", class_="t clearfix")

                # 提取每一天的天气信息
                pattern = re.compile(r'(?=.*\bsky\b)(?=.*\bskyid\b)')
                weather_items = weather_list.find_all("li", class_=pattern)
                weather_data = []
                for item in weather_items:
                    # 提取日期
                    date_tag = item.find("h1")
                    date = date_tag.text.strip()

                    # 提取天气
                    weather_tag = item.find("p", class_="wea")
                    weather = weather_tag["title"]

                    # 提取温度
                    temp_tag = item.find("p", class_="tem")
                    if temp_tag.find("span"):
                        temp_high = temp_tag.find("span").text
                        temp_low = temp_tag.find("i").text
                        temp = f"{temp_high}/{temp_low}"
                    else:
                        temp_low = temp_tag.find("i").text
                        temp = f"{temp_low}"

                    # 提取风向和风力
                    wind_dir_tags = item.find("p", class_="win").find_all("span")
                    wind_dirs = [tag["title"] for tag in wind_dir_tags]
                    wind_force = item.find("p", class_="win").find("i").text

                    # 组合风向和风力
                    wind = f"{', '.join(wind_dirs)} {wind_force}"

                    # 添加到结果列表
                    weather_data.append({
                        "日期": date,
                        "天气": weather,
                        "温度": temp,
                        "风向风力": wind
                    })

                return {
                    "status": "success",
                    "result": weather_data
                }

            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to parse weather data: {str(e)}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to fetch weather data: {str(e)}"
            }

if __name__ == "__main__":
    plugin = WeatherScraperPlugin()
    print(plugin.execute(city_code="101270101"))