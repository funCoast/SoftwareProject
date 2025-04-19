import time

from gtts import gTTS
from pydub import AudioSegment
from pymysql.converters import convert_time

from api.core.plugin.plugins.base_plugin import BasePlugin


def convert_to_wav(input_file, output_file):
    audio = AudioSegment.from_mp3(input_file)
    audio.export(output_file, format="wav")


class TextToSpeechPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name = "TextToSpeech",
            version = "1.0",
            description = "将文本转化为语音",
            intent="Convert_the_text_into_speech",
            param_description={
                "text": "text"
            }
        )

    def execute(self, *args, **kwargs):
        try:
            text = kwargs.get('text')
            language = kwargs.get('language')

            if text is None:
                return {
                    "success": "error",
                    "message": "没有文本输入"
                }

            if language is None:
                language = "zh-cn"

            tts = gTTS(text=text, lang=language)

            tts.save(f"mp3-{time.strftime("%Y%m%d_%H%M%S")}-audio.mp3")

            output_path = "output.wav"
            convert_to_wav(f"mp3-{time.strftime("%Y%m%d_%H%M%S")}-audio.mp3", output_path)

            return {
                "status": "success",
                "result": {
                    "speech_path": output_path
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


if __name__ == '__main__':
    TextToSpeechPlugin().execute(text="原神，启动！", language="zh-cn")