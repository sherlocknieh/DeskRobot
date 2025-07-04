"""
音乐播放模块
模块依赖: pygame

Subscribe:
- PLAY_MUSIC: 开始播放音乐
   data = {
        "path": str,  # 本地文件路径或URL
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
# 本地库
if __name__ != "__main__":
    from .EventBus import EventBus

# 标准库
import logging
import os
import threading
import time
from queue import Queue
from urllib.request import urlretrieve

# 第三方库
import pygame

# 全局变量
logger = logging.getLogger("音乐播放器")
music_files = [os.path.join("localfiles/songs", f) for f in os.listdir("localfiles/songs")]


# 类定义
class MusicPlayer(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True, name="音乐播放器")
        self.event_bus = EventBus()
        self.event_queue = Queue()
        self._stop_event = threading.Event()
        
        # 播放器状态
        self.playback_thread = None
        self.current_player = None
        self.is_playing = False
        self.is_paused = False
        self.temp_files = []
        
        # 播放列表相关属性
        self.playlist = music_files
        self.current_index = 0
        self.volume = 0.5
        
        # 初始化事件订阅
        self.event_bus.subscribe("EXIT", self.event_queue, self.name)
        self.event_bus.subscribe("PLAY_MUSIC", self.event_queue, self.name)
        self.event_bus.subscribe("PAUSE_MUSIC", self.event_queue, self.name)
        self.event_bus.subscribe("STOP_MUSIC", self.event_queue, self.name)
        self.event_bus.subscribe("NEXT_SONG", self.event_queue, self.name)
        self.event_bus.subscribe("PREVIOUS_SONG", self.event_queue, self.name)
        self.event_bus.subscribe("VOLUME_UP", self.event_queue, self.name)
        self.event_bus.subscribe("VOLUME_DOWN", self.event_queue, self.name)

    def run(self):
        # 初始化pygame mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        pygame.mixer.music.set_volume(self.volume)

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
        elif event_type == "VOLUME_UP":
            self.volume = min(1.0, self.volume + 0.1)
            pygame.mixer.music.set_volume(self.volume)
        elif event_type == "VOLUME_DOWN":
            self.volume = max(0.0, self.volume - 0.1)
            pygame.mixer.music.set_volume(self.volume)

    def _handle_play(self, data):
        source = data.get("path")
        source = self.playlist[0] if source is None else source
    
        # 传入列表
        if isinstance(source, list):
            self.playlist = source
            self.current_index = 0
        else: # 传入单个文件
            # 如果文件在当前列表中
            if hasattr(self, "playlist") and source in self.playlist:
                self.current_index = self.playlist.index(source)
            else: # 全新文件
                self.playlist = [source]
                self.current_index = 0

        source = self.playlist[self.current_index] # 从列表中取出歌曲路径

        try:
            # 处理网络资源
            if source.startswith(("http://", "https://")):
                filename = os.path.basename(source)
                local_path, _ = urlretrieve(source, filename)
                self.temp_files.append(local_path)
                source = local_path
    
            # 使用pygame加载音乐
            pygame.mixer.music.load(source)
            self.is_playing = True
            pygame.mixer.music.play()
            self.event_bus.publish("MUSIC_STARTED", self.name)
            
        except Exception as e:
            logger.error(f"播放失败: {e}")
            self.event_bus.publish("ERROR", {"message":str(e)}, self.name)

    def _handle_pause(self):
        #if self.is_playing:
        if not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.event_bus.publish("MUSIC_PAUSED", self.name)
        else:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.event_bus.publish("MUSIC_RESUMED", self.name)
    
    def _handle_stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.event_bus.publish("MUSIC_STOPPED", self.name)

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
            logger.info(f"正在播放: {source}")
            self._handle_play({"path": source})
    
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


# 测试代码
if __name__ == "__main__":
    from EventBus import EventBus
    
    # 创建并启动播放器线程
    player = MusicPlayer()
    player.start()

    # 开始播放
    player.event_bus.publish("PLAY_MUSIC", {"path": music_files})
    time.sleep(3)

    # 切歌控制
    print("下一首歌")
    player.event_bus.publish("NEXT_SONG")
    time.sleep(4)

    print("下一首歌")
    player.event_bus.publish("NEXT_SONG")
    time.sleep(4)

    print("上一首歌")
    player.event_bus.publish("PREVIOUS_SONG")
    time.sleep(4)
    
    # 暂停
    print("暂停播放")
    player.event_bus.publish("PAUSE_MUSIC")
    time.sleep(2)
    
    # 恢复
    print("恢复播放")
    player.event_bus.publish("PAUSE_MUSIC")
    time.sleep(2)
    
    # 停止
    print("停止播放")
    player.event_bus.publish("STOP_MUSIC")

    # 退出播放器
    print("退出播放器")
    player.event_bus.publish("EXIT")
    player.join()
