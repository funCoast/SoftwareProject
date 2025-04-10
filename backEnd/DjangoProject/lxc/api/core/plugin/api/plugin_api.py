from flask import Flask, request, jsonify

from api.core.plugin.managers.plugin_manager import PluginManager

# from managers.plugin_manager import PluginManager

app = Flask(__name__)
plugin_manager = PluginManager()

# TODO 注册插件
# plugin_manager.register_plugin(TimePlugin())
# plugin_manager.register_plugin(WeatherPlugin())
# plugin_manager.register_plugin(WebScraperPlugin())
# plugin_manager.register_plugin(SpeechToTextPlugin())
# plugin_manager.register_plugin(TextToSpeechPlugin())
# plugin_manager.register_plugin(CodeInterpreterPlugin())

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