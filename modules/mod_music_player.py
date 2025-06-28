"""
模块依赖
pip install pydub simpleaudio

# Ubuntu
sudo apt install ffmpeg

# Windows
winget install ffmpeg

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
import pygame

if __name__ != "__main__":
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
        self.playback_thread = None
        self.current_player = None
        self.is_playing = False
        self.is_paused = False
        self.loop = False
        self.temp_files = []
        
        # 新增播放列表相关属性
        self.playlist = []
        self.current_index = 0
        self.volume = 0.5
        
        # 初始化pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume)
        
        # 新增事件订阅
        self.event_bus.subscribe("NEXT_SONG", self.event_queue, self.name)
        self.event_bus.subscribe("PREVIOUS_SONG", self.event_queue, self.name)

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
        elif event_type == "NEXT_SONG":
            self._handle_next()
        elif event_type == "PREVIOUS_SONG":
            self._handle_previous()

    def _handle_play(self, data):
        source = data.get("path")
        self.loop = data.get("loop", False)

        # 新增播放列表支持
        if isinstance(source, list):
            self.playlist = source
            self.current_index = 0
            source = self.playlist[self.current_index]
        else:
            self.playlist = [source]
            self.current_index = 0

        try:
            # 统一处理本地和网络资源
            if source.startswith(("http://", "https://")):
                filename = os.path.basename(source)
                local_path, _ = urlretrieve(source, filename)
                self.temp_files.append(local_path)
                source = local_path

            # 使用pygame加载音乐
            pygame.mixer.music.load(source)
            self.is_playing = True
            pygame.mixer.music.play(loops=-1 if self.loop else 0)
            self.event_bus.publish("MUSIC_STARTED", source=source)
            
        except Exception as e:
            logger.error(f"播放失败: {e}")
            self.event_bus.publish("ERROR", {"message":str(e)})

    def _handle_pause(self):
        if self.is_playing:
            if not self.is_paused:
                pygame.mixer.music.pause()
                self.is_paused = True
                self.event_bus.publish("MUSIC_PAUSED")
            else:
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.event_bus.publish("MUSIC_RESUMED")
    def _handle_stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.event_bus.publish("MUSIC_STOPPED")

    def _handle_next(self):
        if len(self.playlist) == 0:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self._play_by_index()

    def _handle_previous(self):
        if len(self.playlist) == 0:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self._play_by_index()

    def _play_by_index(self):
        if 0 <= self.current_index < len(self.playlist):
            source = self.playlist[self.current_index]
            self._handle_play({"path": source, "loop": self.loop})
    def stop(self):
        """新增清理方法"""
        self._handle_stop()
        self._stop_event.set()
        # 清理临时文件
        for f in self.temp_files:
            try:
                os.remove(f)
            except:
                pass
if __name__ == "__main__":
    # 测试代码
    import numpy as np
    from EventBus import EventBus
    
    import os
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    music_path = os.path.join(project_root, "tools/Creamy.ogg")
    
    # 生成测试音频
    sample_rate = 44100
    duration = 2  # 秒
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(440 * 2 * np.pi * t)
    audio = np.int16(tone * 32767)
    
    # 转为立体声（2列）
    audio = np.column_stack((audio, audio))
    
    pygame.mixer.init()
    sound = pygame.sndarray.make_sound(audio)

    # 保存为WAV格式
    #sound.save("test.wav")
    import scipy.io.wavfile
    audio = np.column_stack((audio, audio))
    scipy.io.wavfile.write("test.wav", sample_rate, audio)

    
    # 创建并启动播放器线程
    player = MusicPlayerThread()
    player.start()

    # 播放单个文件
    player.event_bus.publish("PLAY_MUSIC", {"path": "test.wav"})

    # 播放列表 
    player.event_bus.publish("PLAY_MUSIC", {"path": ["song1.wav", "song2.wav", "song3.wav"]})

    # 切歌控制
    player.event_bus.publish("NEXT_SONG")
    player.event_bus.publish("PREVIOUS_SONG")

    
    # 测试暂停
    print("暂停播放")
    player.player.event_bus.publish("PAUSE_MUSIC")
    time.sleep(2)
    
    # 测试恢复
    print("恢复播放")
    player.player.event_bus.publish("PAUSE_MUSIC")
    time.sleep(2)
    
    # 停止播放
    print("停止播放")
    player.player.event_bus.publish("STOP_MUSIC")

    # 退出播放器
    print("退出播放器")
    player.player.event_bus.publish("EXIT")
    player.join()
