import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages') # 为 picamera2 引入系统库路径
from picamera2 import Picamera2
sys.path.pop(0)  # 导入 picamera2 后立即移除系统库路径，避免影响其他模块
import cv2


# 初始化摄像头
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
picam2.start()

while True:
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

picam2.stop()
cv2.destroyAllWindows()

