import logging

import edge_tts


class EdgeTTS:
    def __init__(self):
        pass

    def text_to_speech_mp3(
        self,
        text: str,
        voice: str = "zh-CN-XiaoxiaoNeural",
        output_path: str = "output.mp3",
    ) -> str:
        """
        使用 edge-tts 将文本转换为语音并保存为 MP3 文件。

        :param text: 要转换的文本
        :param voice: 语音类型，默认为 "zh-CN-XiaoxiaoNeural"
        :param output_path: 输出文件路径，默认为 "output.mp3"
        :return: 输出文件的路径
        """
        try:
            communicate = edge_tts.Communicate(text, voice)
            communicate.save_sync(output_path)
            return output_path
        except Exception as e:
            logging.error(f"Error during text to speech conversion: {e}")
            return None


if __name__ == "__main__":
    tts = EdgeTTS()
    text = "你好，世界！"
    output_file = tts.text_to_speech_mp3(
        text, voice="zh-CN-XiaoxiaoNeural", output_path="output.mp3"
    )
