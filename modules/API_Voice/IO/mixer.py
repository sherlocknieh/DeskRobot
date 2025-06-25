import threading
import numpy as np
from queue import Queue
import time


class AudioMixer(threading.Thread):
    def on_track_finished(self, track_id):
        """音轨播放完毕时的回调（由上层注入）。"""
        pass
    def add_stream_from_file(self, track_id, file_path):
        """
        从音频文件添加音轨，支持 wav/ogg/mp3。自动转为 bytes 并分块。
        需保证文件参数与 mixer 统一（采样率、通道数、位宽），否则需预处理！
        """
        import wave
        import os
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.wav':
            with wave.open(file_path, 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
            self.add_stream(track_id, frames)
        elif ext == '.ogg':
            try:
                from pydub import AudioSegment
            except ImportError:
                raise RuntimeError('需要安装 pydub 才能加载 ogg 文件')
            audio = AudioSegment.from_ogg(file_path)
            audio = audio.set_frame_rate(self.voice_io.rate).set_channels(self.voice_io.channels).set_sample_width(2)
            self.add_stream(track_id, audio.raw_data)
        elif ext == '.mp3':
            try:
                from pydub import AudioSegment
            except ImportError:
                raise RuntimeError('需要安装 pydub 才能加载 mp3 文件')
            audio = AudioSegment.from_mp3(file_path)
            audio = audio.set_frame_rate(self.voice_io.rate).set_channels(self.voice_io.channels).set_sample_width(2)
            self.add_stream(track_id, audio.raw_data)
        else:
            raise ValueError(f'不支持的音频格式: {ext}')
    """
    简单音频混音器模板：
    - 支持多路音轨（每路一个唯一track_id）
    - 所有音轨参数需一致（采样率、通道数、位宽）
    - 所有音频数据需为int16、bytes格式
    - 统一输出到VoiceIO
    """
    def __init__(self, voice_io, chunk_size=1024):
        super().__init__(daemon=True)
        self.voice_io = voice_io
        self.chunk_size = chunk_size
        self.tracks = {}  # track_id: Queue
        self.paused = set()  # 被暂停的track_id集合
        self.lock = threading.Lock()
        self.running = threading.Event()
        self.running.set()
    def pause_stream(self, track_id):
        """暂停某条音轨（不移除队列，仅不参与混音）"""
        with self.lock:
            self.paused.add(track_id)

    def resume_stream(self, track_id):
        """恢复某条音轨的混音"""
        with self.lock:
            self.paused.discard(track_id)

    def add_stream(self, track_id, audio_bytes):
        """添加一条音轨，audio_bytes为bytes或分段bytes列表"""
        q = Queue()
        if isinstance(audio_bytes, bytes):
            for i in range(0, len(audio_bytes), self.chunk_size*2):
                q.put(audio_bytes[i:i+self.chunk_size*2])
        elif isinstance(audio_bytes, list):
            for chunk in audio_bytes:
                q.put(chunk)
        with self.lock:
            self.tracks[track_id] = q

    def remove_stream(self, track_id):
        """停止并移除某条音轨"""
        with self.lock:
            if track_id in self.tracks:
                del self.tracks[track_id]

    def run(self):
        while self.running.is_set():
            finished_tracks = []
            with self.lock:
                active_items = [(tid, q) for tid, q in self.tracks.items() if tid not in self.paused]
            if not active_items:
                time.sleep(0.01)
                continue
            chunks = []
            for tid, q in active_items:
                if not q.empty():
                    chunk = q.get()
                    arr = np.frombuffer(chunk, dtype=np.int16)
                    chunks.append(arr)
                else:
                    # 队列已空，音轨播放完毕
                    finished_tracks.append(tid)
            if chunks:
                maxlen = max(len(c) for c in chunks)
                chunks = [np.pad(c, (0, maxlen - len(c))) for c in chunks]
                mixed = np.sum(chunks, axis=0)
                mixed = np.clip(mixed, -32768, 32767)
                self.voice_io.play_audio_chunk(mixed.astype(np.int16).tobytes())
            else:
                time.sleep(0.01)
            # 处理播放完毕的音轨
            for tid in finished_tracks:
                with self.lock:
                    if tid in self.tracks:
                        del self.tracks[tid]
                if hasattr(self, 'on_track_finished') and callable(self.on_track_finished):
                    self.on_track_finished(tid)

    def stop(self):
        self.running.clear()

# 用法示例：
# from .io import VoiceIO
# voice_io = VoiceIO()
# mixer = AudioMixer(voice_io)
# mixer.start()
# mixer.add_stream('music', music_bytes)
# mixer.add_stream('tts', tts_bytes)
# mixer.stop_stream('music')
# mixer.stop()


if __name__ == "__main__":
    from .io import VoiceIO
    voice_io = VoiceIO()
    mixer = AudioMixer(voice_io)
    mixer.start()
    # 添加音轨示例
    music_path = "Creamy.ogg"
    record_path = "test_recording.wav"



    mixer.add_stream_from_file('music', music_path)
    mixer.add_stream_from_file('tts', record_path)
    # 停止音轨示例

    time.sleep(2)  # 等待音频播放
    mixer.remove_stream('music')

    time.sleep(2)  # 等待音频播放完成
    mixer.stop()
