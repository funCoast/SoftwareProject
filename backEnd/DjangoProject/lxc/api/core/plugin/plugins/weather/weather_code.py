import xml.etree.ElementTree as ET

# 英文城市名 -> 中文城市名 映射表
english_to_chinese = {
    "Beijing": "北京",
    "Shanghai": "上海",
    "Tianjin": "天津",
    "Chongqing": "重庆",
    "Harbin": "哈尔滨",
    "Shenzhen": "深圳",
    "Guangzhou": "广州",
    "Hangzhou": "杭州",
    "Nanjing": "南京",
    "Suzhou": "苏州",
    "Chengdu": "成都",
    "Wuhan": "武汉",
    "Xi'an": "西安",
    "Changsha": "长沙",
    "Zhengzhou": "郑州",
    "Shenyang": "沈阳",
    "Qingdao": "青岛",
    "Dalian": "大连",
    "Jinan": "济南",
    "Xiamen": "厦门",
    "Fuzhou": "福州",
    "Ningbo": "宁波",
    # 可以根据需要继续添加
}

# 解析 XML 文件，生成 中文城市名 -> 天气代码 的映射表
def build_city_weathercode_map(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    city_to_weather_code = {}

    for province in root.findall('province'):
        for city in province.findall('city'):
            city_name = city.get('name')
            for county in city.findall('county'):
                county_name = county.get('name')
                weather_code = county.get('weatherCode')
                if county_name == city_name:
                    city_to_weather_code[city_name] = weather_code
    return city_to_weather_code

# 主查询函数
def get_weather_code(english_city_name, city_to_weather_code):
    chinese_city_name = english_to_chinese.get(english_city_name)
    if not chinese_city_name:
        return f"City '{english_city_name}' not found in English-Chinese mapping."

    weather_code = city_to_weather_code.get(chinese_city_name)
    if not weather_code:
        return f"City '{chinese_city_name}' not found in weather code database."

    return weather_code

if __name__ == "__main__":
    xml_file = "./weatherCode.xml"  # 你的xml文件路径
    city_to_weather_code = build_city_weathercode_map(xml_file)

    # 示例输入
    city_input = input("Please enter the English name of the city: ").strip()
    result = get_weather_code(city_input, city_to_weather_code)
    print(f"Result: {result}")
