import base64
import hashlib
import hmac
import json
import logging
import queue
import ssl
import threading
import time
from datetime import datetime
from time import mktime
from urllib.parse import urlencode, urlparse
from wsgiref.handlers import format_date_time

import websocket

logger = logging.getLogger(__name__)

# 全局变量来存储最终识别结果和控制流程
final_result = ""
result_lock = threading.Lock()
transcription_finished = threading.Event()


class IflytekSTTClient:
    def __init__(self, appid, apikey, apisecret):
        self.appid = appid
        self.apikey = apikey
        self.apisecret = apisecret
        self.url = "wss://iat-api.xfyun.cn/v2/iat"
        self.host = urlparse(self.url).hostname
        self.path = urlparse(self.url).path
        self.result_queue = queue.Queue()

    def _get_auth_url(self):
        # 构造鉴权url
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = f"host: {self.host}\n"
        signature_origin += f"date: {date}\n"
        signature_origin += f"GET {self.path} HTTP/1.1"

        signature_sha = hmac.new(
            self.apisecret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode("utf-8")

        authorization_origin = (
            f'api_key="{self.apikey}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature_sha_base64}"'
        )
        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode(
            "utf-8"
        )

        v = {"authorization": authorization, "date": date, "host": self.host}
        url = self.url + "?" + urlencode(v)
        return url

    def _on_message(self, ws, message):
        global final_result
        try:
            msg = json.loads(message)
            code = msg.get("code")
            sid = msg.get("sid")
            data = msg.get("data", {})
            status = data.get("status")
            result_data = data.get("result", {})

            if code != 0:
                logger.error(f"WebSocket error received: code={code}, message={msg}")
                transcription_finished.set()
                return

            text = ""
            for i in result_data.get("ws", []):
                for w in i.get("cw", []):
                    text += w.get("w", "")

            # 使用pgs字段进行动态修正结果的处理
            if result_data.get("pgs") == "rpl":
                from_index = result_data["rg"][0] - 1
                to_index = result_data["rg"][1] - 1
                with result_lock:
                    result_list = list(final_result)
                    result_list[from_index : to_index + 1] = list(text)
                    final_result = "".join(result_list)
            else:
                with result_lock:
                    final_result += text

            if status == 2:  # Frame status: 2 means this is the last frame
                logger.info("Last frame received from Iflytek.")
                ws.close()
                transcription_finished.set()

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            transcription_finished.set()

    def _on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")
        transcription_finished.set()

    def _on_close(self, ws, close_status_code, close_msg):
        logger.info(
            f"WebSocket connection closed: code={close_status_code}, msg={close_msg}"
        )
        transcription_finished.set()

    def _on_open(self, ws, audio_file_path):
        def run(*args):
            frame_size = 1280  # 80ms
            intervel = 0.04  # 40ms
            status = (
                0  # Frame status: 0 for first frame, 1 for intermediate, 2 for last
            )

            with open(audio_file_path, "rb") as f:
                while True:
                    buf = f.read(frame_size)
                    # First frame
                    if status == 0:
                        data = {
                            "common": {"app_id": self.appid},
                            "business": {
                                "language": "zh_cn",
                                "domain": "iat",
                                "accent": "mandarin",
                                "dwa": "wpgs",  # 开启动态修正
                            },
                            "data": {
                                "status": 0,
                                "format": "audio/L16;rate=16000",
                                "encoding": "raw",
                                "audio": base64.b64encode(buf).decode("utf-8"),
                            },
                        }
                        status = 1  # Move to intermediate frame status

                    # Intermediate and last frames
                    else:
                        # Determine if this is the last frame
                        if not buf or len(buf) < frame_size:
                            status = 2

                        data = {
                            "data": {
                                "status": status,
                                "audio": base64.b64encode(buf).decode("utf-8"),
                            }
                        }

                    ws.send(json.dumps(data))

                    if status == 2:
                        logger.info("Sent last audio frame to Iflytek.")
                        break

                    time.sleep(intervel)

        threading.Thread(target=run).start()

    def speech_to_text_from_file(self, audio_file_path: str) -> str:
        global final_result, transcription_finished

        # Reset state for a new transcription
        final_result = ""
        transcription_finished.clear()

        ws_url = self._get_auth_url()
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        ws.on_open = lambda ws: self._on_open(ws, audio_file_path)

        ws_thread = threading.Thread(
            target=ws.run_forever, kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}}
        )
        ws_thread.daemon = True
        ws_thread.start()

        # Wait for the transcription to finish or timeout
        finished = transcription_finished.wait(timeout=15)
        if not finished:
            logger.warning("Transcription timed out.")
            ws.close()

        with result_lock:
            return final_result
