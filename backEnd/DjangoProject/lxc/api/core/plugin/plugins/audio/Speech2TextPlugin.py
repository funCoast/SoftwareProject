import speech_recognition as sr
from pydub import AudioSegment
import os
import uuid

from api.core.plugin.plugins.base_plugin import BasePlugin


class SpeechToTextPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name = "SpeechToTextPlugin",
            version = "1.0",
            description = "将语音音频转换为文本",
            intent="Convert voice audio to text"
        )

    def convert_audio_to_wav(self, audio_path):
        if audio_path.endswith('.mp3'):
            sound = AudioSegment.from_mp3(audio_path)
            wav_path = audio_path.replace('.mp3', f'_{uuid.uuid4().hex}.wav')
            sound.export(wav_path, format="wav")
            return wav_path
        return audio_path

    def execute(self, *args, **kwargs):
        # 转换格式
        audio_path = kwargs['audio_path']

        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language='zh-CN')  # 可改为 'en-US' 等
                return {"text": text}
        except sr.UnknownValueError:
            return {"error": "无法识别语音"}
        except sr.RequestError as e:
            return {"error": f"识别服务请求失败: {e}"}
        finally:
            if audio_path != audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
