from api.core.plugin.plugins.weather.weather_scraper_plugin import WeatherScraperPlugin
from ...registry import register_node
import json

@register_node("weather")
def run_plugin_node(node,inputs):
    city = inputs[0].get("value")
    plugin = WeatherScraperPlugin()
    data = plugin.execute(city_code=city)
    result_list = data['result']  # 取出 result 部分，是个列表
    result_str = json.dumps(result_list, ensure_ascii=False)  # 转成字符串
    outputs = {}
    for output in node.get("outputs", []):
        id = output["id"]
        outputs[id] = result_str  # 所有输出都给一样的结果（你也可以按 name 分别生成）
    return outputs