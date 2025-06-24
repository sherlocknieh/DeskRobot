"""
模块依赖
pip install pydub simpleaudio

# Ubuntu
sudo apt install ffmpeg

# Windows (通过choco)
choco install ffmpeg

音乐播放模块

Subscribe:
- PLAY_MUSIC: 开始播放音乐
    - data格式:
    {
        "path": str,  # 本地文件路径或URL
        "loop": bool   # 是否循环播放（可选）
    }
- PAUSE_MUSIC: 暂停/恢复播放
- STOP_MUSIC: 停止播放
- EXIT: 停止线程

Publish:
- MUSIC_STARTED: 音乐开始播放时发布
- MUSIC_PAUSED: 音乐暂停时发布  
- MUSIC_STOPPED: 音乐停止时发布
- ERROR: 发生错误时发布
"""

import logging
import os
import threading
import time
from queue import Queue
from urllib.request import urlretrieve
from pydub import AudioSegment
from pydub.playback import play

from .EventBus import EventBus

logger = logging.getLogger("音乐播放器")

class MusicPlayerThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True, name="MusicPlayerThread")
        self.event_bus = EventBus()
        self.event_queue = Queue()
        self._stop_event = threading.Event()
        
        # 初始化事件订阅
        self.event_bus.subscribe("PLAY_MUSIC", self.event_queue, self.name)
        self.event_bus.subscribe("PAUSE_MUSIC", self.event_queue, self.name)
        self.event_bus.subscribe("STOP_MUSIC", self.event_queue, self.name)
        self.event_bus.subscribe("EXIT", self.event_queue, self.name)
        
        # 播放器状态
        self.current_player = None
        self.is_playing = False
        self.is_paused = False
        self.loop = False
        self.temp_files = []

    def run(self):
        while not self._stop_event.is_set():
            try:
                event = self.event_queue.get(timeout=1)
                self._handle_event(event)
            except Exception as e:
                logger.debug(f"Queue get timeout: {e}")
                
    def _handle_event(self, event):
        event_type = event.get("type")
        data = event.get("data", {})

        if event_type == "PLAY_MUSIC":
            self._handle_play(data)
        elif event_type == "PAUSE_MUSIC":
            self._handle_pause()
        elif event_type == "STOP_MUSIC":
            self._handle_stop()
        elif event_type == "EXIT":
            self.stop()

    def _handle_play(self, data):
        source = data.get("path")
        self.loop = data.get("loop", False)

        try:
            # 如果是网络资源则下载
            if source.startswith(("http://", "https://")):
                filename = os.path.basename(source)
                local_path, _ = urlretrieve(source, filename)
                self.temp_files.append(local_path)
                audio = AudioSegment.from_file(local_path)
            else:
                audio = AudioSegment.from_file(source)

            self._stop_playback()
            
            self.current_player = audio
            self.is_playing = True
            self._play_audio()
            
            self.event_bus.publish("MUSIC_STARTED", source=source)
        except Exception as e:
            logger.error(f"播放失败: {e}")
            self.event_bus.publish("ERROR", message=str(e))

    def _play_audio(self):
        def playback():
            try:
                while self.is_playing and not self._stop_event.is_set():
                    play(self.current_player)
                    if not self.loop:
                        break
                self._stop_playback()
            except Exception as e:
                logger.error(f"播放错误: {e}")

        self.playback_thread = threading.Thread(target=playback)
        self.playback_thread.start()

    def _handle_pause(self):
        if self.is_playing:
            if self.is_paused:
                self.is_paused = False
                self.event_bus.publish("MUSIC_RESUMED")
            else:
                self.is_paused = True
                self.event_bus.publish("MUSIC_PAUSED")

    def _handle_stop(self):
        self._stop_playback()
        self.event_bus.publish("MUSIC_STOPPED")

    def _stop_playback(self):
        self.is_playing = False
        self.is_paused = False
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join()

    def stop(self):
        """停止线程并清理资源"""
        self._stop_event.set()
        self._stop_playback()
        for f in self.temp_files:
            try:
                os.remove(f)
            except:
                pass

if __name__ == "__main__":
    # 测试代码
    from pydub import generators
    
    # 生成测试音频
    test_sound = generators.Sine(440).to_audio_segment(duration=2000)
    test_sound.export("test.mp3", format="mp3")

    # 初始化事件总线
    event_bus = EventBus()
    
    # 创建并启动播放器线程
    player = MusicPlayerThread(event_bus)
    player.start()

    # 测试播放
    event_bus.publish("PLAY_MUSIC", path="test.mp3")
    time.sleep(5)
    
    # 测试暂停
    event_bus.publish("PAUSE_MUSIC")
    time.sleep(2)
    
    # 测试恢复
    event_bus.publish("PAUSE_MUSIC")
    time.sleep(2)
    
    # 停止播放
    event_bus.publish("STOP_MUSIC")
    player.join()
