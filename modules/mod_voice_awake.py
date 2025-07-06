"""
语音唤醒模块（基于openWakeWord实现）
实现语音唤醒词检测和打断检测功能
"""

from modules.EventBus import EventBus
from modules.mod_voice_io import VoiceIO


import logging
import threading
from queue import Queue
logger = logging.getLogger("语音唤醒")


import numpy as np
logger.info("正在导入 openWakeWord Model...")
from openwakeword.model import Model
from openwakeword.utils import download_models




class AwakeThread(threading.Thread):
    """
    唤醒词检测线程，集成openWakeWord实现实时唤醒检测
    """
    def __init__(self, wakeword_models=["hey jarvis"], threshold=0.6):
        super().__init__(daemon=True, name="语音唤醒")
        self.event_bus = EventBus()
        self.stop_event = threading.Event()
        self.event_queue = Queue()
        
        # 初始化参数
        self.wakeword_models = wakeword_models
        self.threshold = threshold
        self.is_speaking_tts = False  # TTS播放状态
        
        # 初始化openWakeWord
        self.oww_model = None
        self.voice_io = None  # 复用现有的VoiceIO实例
        
        # 事件订阅
        self.event_bus.subscribe("TTS_STARTED", self.event_queue, self.name)
        self.event_bus.subscribe("TTS_FINISHED", self.event_queue, self.name)
        self.event_bus.subscribe("EXIT", self.event_queue, self.name)
        
        logger.info("唤醒模块初始化完成")

    def _setup(self):
        """初始化音频设备和唤醒模型"""
        try:
            # 自动下载预训练模型

            logger.info("下载预训练模型")
            download_models(["hey_jarvis"])
            # 初始化openWakeWord模型
            self.oww_model = Model(
                wakeword_models = self.wakeword_models,  # 预训练模型路径
                vad_threshold = 0.4,              # 语音活动检测阈值
                enable_speex_noise_suppression = True
            )
            logger.info("模型加载完成")
            
            # 复用现有的音频输入设备
            self.voice_io = VoiceIO(
                rate=16000,
                channels=1,
                frames_per_buffer=1280  # 匹配openWakeWord的80ms帧
            )
            
            logger.info("唤醒模型加载成功")
            return True
        except Exception as e:
            logger.error(f"初始化失败: {e}", exc_info=True)
            return False

    def run(self):
        """主检测循环"""
        if not self._setup():
            return
        
        threading.Thread(target=self._event_loop, daemon=True, name="事件处理").start()
        
        logger.info("开始监听唤醒词...")
        last_score = 0.0
        while not self.stop_event.is_set():
            # 获取音频数据
            audio_data = self.voice_io.record_chunk()
            if not audio_data:
                continue
                
            # 转换为int16数组
            frame = np.frombuffer(audio_data, dtype=np.int16)
            
            # 获取预测结果
            prediction = self.oww_model.predict(frame)
            # print(prediction) {'hey_jarvis': 0.0}
            
            for name, score in prediction.items():
                if last_score < self.threshold and score >= self.threshold:
                    logger.info(f"检测到唤醒词: {name} (得分: {score:.2f})")
                    self.event_bus.publish("WAKE_WORD_DETECTED", self.name)
                last_score = score

    def _event_loop(self):
        """处理事件总线消息"""
        while True:
            event = self.event_queue.get()
            if event["type"] == "TTS_STARTED":
                self.is_speaking_tts = True
                logger.debug("进入打断模式")
            elif event["type"] == "TTS_FINISHED":
                self.is_speaking_tts = False
                logger.debug("返回监听模式")
            elif event["type"] == "EXIT":
                self.stop_event.set()
                logger.info("收到退出信号")
                break

    def stop(self):
        """安全停止线程"""
        self.stop_event.set()
        self.oww_model = None
        logger.info("唤醒模块已停止")
