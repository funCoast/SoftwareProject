from api.core.plugin.plugins.audio.Speech2TextPlugin import SpeechToTextPlugin
from api.core.plugin.plugins.code.code_run_plugin import CodeRunPlugin
from api.core.plugin.plugins.time.current_time_plugin import CurrentTimePlugin
from api.core.plugin.plugins.time.timestamp_pulgin import TimestampPlugin
from api.core.plugin.plugins.time.timestamp_transform_plugin import TimestampTransformPlugin
from api.core.plugin.plugins.time.timezoen_switch_plugin import TimezoneSwitchPlugin
from api.core.plugin.plugins.time.weekday_calculator_plugin import WeekdayCalculatorPlugin
from api.core.plugin.plugins.weather.weather_scraper_plugin import WeatherScraperPlugin


def register_plugins(plugin_manager):
    plugin_manager.register_plugin(CurrentTimePlugin)
    plugin_manager.register_plugin(TimestampPlugin)
    plugin_manager.register_plugin(TimestampTransformPlugin)
    plugin_manager.register_plugin(TimezoneSwitchPlugin)
    plugin_manager.register_plugin(WeekdayCalculatorPlugin)
    plugin_manager.register_plugin(CodeRunPlugin)
    plugin_manager.register_plugin(SpeechToTextPlugin)
    plugin_manager.register_plugin(WeatherScraperPlugin)