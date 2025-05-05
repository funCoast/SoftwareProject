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

    # 1. county_map：county_name → weatherCode
    # 2. city_map：city_name → 第一个 county 的 weatherCode
    # 3. prov_map：province_name → 第一个 city 的第一个 county 的 weatherCode
    county_map = {}
    city_map = {}
    prov_map = {}

    for prov in root.findall('province'):
        prov_name = prov.get('name')
        first_city_code = None

        # 遍历该省下所有 city
        for city in prov.findall('city'):
            city_name = city.get('name')
            # 该市的第一个 county
            first_county = city.find('county')
            if first_county is not None:
                first_county_code = first_county.get('weatherCode')
                # 如果还没给省级做过映射，则用这个市的第一个 county
                if first_city_code is None:
                    first_city_code = first_county_code
                # 记录 city → code
                city_map.setdefault(city_name, first_county_code)

            # 遍历该市所有 county，记录 county → code
            for county in city.findall('county'):
                county_name = county.get('name')
                county_code = county.get('weatherCode')
                county_map[county_name] = county_code

        # 记录 province → code
        if first_city_code is not None:
            prov_map[prov_name] = first_city_code

    # 合并三张表：查询时先查 county_map，再 city_map，最后 prov_map
    # 也可以直接合并到一个 dict，用插入顺序保证优先级：
    full_map = {}
    # 先省，后市，最后县，这样查询时 dict.get(name) 就自动获得最高优先级的值
    full_map.update(prov_map)   # 省级兜底
    full_map.update(city_map)   # 覆盖省级
    full_map.update(county_map) # 覆盖市级和省级

    return full_map

# 主查询函数
def get_weather_code_en(english_city_name, city_to_weather_code):
    chinese_city_name = english_to_chinese.get(english_city_name)
    if not chinese_city_name:
        return f"City '{english_city_name}' not found in English-Chinese mapping."

    weather_code = city_to_weather_code.get(chinese_city_name)
    if not weather_code:
        return f"City '{chinese_city_name}' not found in weather code database."

    return weather_code

def get_weather_code_ch(chinese_city_name, city_to_weather_code):
    weather_code = city_to_weather_code.get(chinese_city_name)
    if not weather_code:
        return f"City '{chinese_city_name}' not found in weather code database."
    return weather_code

if __name__ == "__main__":
    xml_file = "./weatherCode.xml"  # 你的xml文件路径
    city_to_weather_code = build_city_weathercode_map(xml_file)
    print(city_to_weather_code)
    result = get_weather_code_ch("海淀", city_to_weather_code)
    print(f"Result: {result}")
