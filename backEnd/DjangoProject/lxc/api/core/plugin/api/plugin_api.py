from flask import Flask, request, jsonify

from api.core.plugin.managers.plugin_manager import PluginManager
from api.core.plugin.plugins.audio.Speech2TextPlugin import SpeechToTextPlugin
from api.core.plugin.plugins.code.code_run_plugin import CodeRunPlugin
from api.core.plugin.plugins.time.current_time_plugin import CurrentTimePlugin
from api.core.plugin.plugins.time.timestamp_pulgin import TimestampPlugin
from api.core.plugin.plugins.time.timestamp_transform_plugin import TimestampTransformPlugin
from api.core.plugin.plugins.time.timezoen_switch_plugin import TimezoneSwitchPlugin
from api.core.plugin.plugins.time.weekday_calculator_plugin import WeekdayCalculatorPlugin
from api.core.plugin.plugins.weather.WeatherForecastPlugin import WeatherScraperPlugin

app = Flask(__name__)
plugin_manager = PluginManager()

plugin_manager.register_plugin(CurrentTimePlugin)
plugin_manager.register_plugin(TimestampPlugin)
plugin_manager.register_plugin(TimestampTransformPlugin)
plugin_manager.register_plugin(TimezoneSwitchPlugin)
plugin_manager.register_plugin(WeekdayCalculatorPlugin)
plugin_manager.register_plugin(CodeRunPlugin)
plugin_manager.register_plugin(SpeechToTextPlugin)
plugin_manager.register_plugin(WeatherScraperPlugin)

@app.route('/plugins', methods=['GET'])
def list_plugins():
    plugins = [{"name": name, "description": plugin.description} for name, plugin in plugin_manager.plugins.items()]
    return jsonify(plugins)

@app.route('/plugins/<plugin_name>/execute', methods=['POST'])
def execute_plugin(plugin_name):
    try:
        data = request.json
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        result = plugin_manager.execute_plugin(plugin_name, *args, **kwargs)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)