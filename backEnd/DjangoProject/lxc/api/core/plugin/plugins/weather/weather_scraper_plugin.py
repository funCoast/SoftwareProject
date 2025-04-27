import os

import requests
from bs4 import BeautifulSoup
from api.core.plugin.plugins.base_plugin import BasePlugin
from api.core.plugin.plugins.weather.weather_code import get_weather_code, build_city_weathercode_map


class WeatherScraperPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="WeatherScraperPlugin",
            version="1.0",
            description="得到天气",
            intent="Check_the_weather_according_to_the_city",
            param_description={
                "city": "the city for which weather information is requested. Default: None"
            }
        )

    def fetch_weather_page(self, city_code):
        url = f"https://www.weather.com.cn/weather/{city_code}.shtml"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/113.0.0.0 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.encoding = 'utf-8'  # 必须设编码
            if response.status_code == 200:
                return response.text
            else:
                raise Exception(f"HTTP {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to fetch weather page: {str(e)}")

    def parse_weather_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        weather_list = soup.find("ul", class_="t clearfix")
        if not weather_list:
            raise Exception("Failed to find weather list on page.")

        weather_data = []
        weather_items = weather_list.find_all("li")
        for item in weather_items:
            try:
                # 日期
                date = item.find("h1").text.strip()

                # 天气
                weather_tag = item.find("p", class_="wea")
                weather = weather_tag.text.strip() if weather_tag else ""

                # 温度
                temp_tag = item.find("p", class_="tem")
                high = temp_tag.find("span").text if temp_tag.find("span") else ""
                low = temp_tag.find("i").text if temp_tag.find("i") else ""
                temp = f"{high}/{low}" if high else low

                # 风向风力
                win_tag = item.find("p", class_="win")
                wind_dirs = [span["title"] for span in win_tag.find_all("span")] if win_tag else []
                wind_force = win_tag.find("i").text if win_tag and win_tag.find("i") else ""
                wind = f"{', '.join(wind_dirs)} {wind_force}".strip()

                weather_data.append({
                    "日期": date,
                    "天气": weather,
                    "温度": temp,
                    "风向风力": wind
                })
            except Exception:
                continue  # 有些<li>可能结构不完整，直接跳过

        return weather_data

    def execute(self, *args, **kwargs):
        try:
            city_code = kwargs.get('city_code')
            if not city_code:
                return {"status": "error", "message": "Missing 'city_code' parameter"}

            if not city_code.isdigit():
                # city_code实际上是城市名，需要转换
                current_dir = os.path.dirname(os.path.abspath(__file__))
                xml_file = os.path.join(current_dir, "weatherCode.xml")

                city_map = build_city_weathercode_map(xml_file)
                city_code = get_weather_code(city_code, city_map)

            html = self.fetch_weather_page(city_code)
            weather_data = self.parse_weather_html(html)

            return {"status": "success", "result": weather_data}
        except Exception as e:
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    plugin = WeatherScraperPlugin()
    print(plugin.execute(city_code="Beijing"))  # 测试一下北京
