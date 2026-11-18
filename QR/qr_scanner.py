import time
import cv2
import numpy as np

# opencv qr detector
qr_detector = cv2.QRCodeDetector()


# scans a camera frame to find and decode qr code
def scan_frame(frame: np.ndarray) -> tuple[str, np.ndarray]:
    if frame is None:
        return "", None
    decoded_text, points, _ = qr_detector.detectAndDecode(frame)
    if points is not None and len(points) > 0:
        return decoded_text.strip(), points
    return "", None


# draws green box around qr code on video
def draw_qr_box(frame: np.ndarray, points: np.ndarray) -> np.ndarray:
    if points is not None:
        pts = points.astype(int).reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
    return frame


# prevents the camera from scanning the same student over and over every second
class ScanCooldown:
    def __init__(self, cooldown_seconds: int = 4):
        self.cooldown_seconds = cooldown_seconds
        self.last_scans: dict[int, float] = {}

    def can_scan(self, student_id: int) -> bool:
        now = time.time()
        last_time = self.last_scans.get(student_id, 0)
        if now - last_time >= self.cooldown_seconds:
            self.last_scans[student_id] = now
            return True
        return False
