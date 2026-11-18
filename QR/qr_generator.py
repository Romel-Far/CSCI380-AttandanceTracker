import io
import qrcode
from PIL import Image
from PyQt6.QtGui import QImage, QPixmap


# formats student info into a string for the qr code
def create_student_qr_data(student_id: int, student_name: str) -> str:
    if not isinstance(student_id, int) or student_id <= 0:
        raise ValueError("student_id must be a positive integer.")
    clean_name = student_name.strip()
    if not clean_name:
        raise ValueError("student_name cannot be empty.")
    return f"STUDENT:{student_id}:{clean_name}"


# parses the scanned text back into id and name
def parse_student_qr_data(raw_text: str) -> dict:
    parts = raw_text.strip().split(":")
    if len(parts) != 3 or parts[0] != "STUDENT":
        return None
    try:
        return {"student_id": int(parts[1]), "student_name": parts[2]}
    except ValueError:
        return None


# makes the qr code image
def generate_qr_image(data_text: str, save_path: str = "") -> Image.Image:
    if not data_text:
        raise ValueError("data_text cannot be empty.")
    img = qrcode.make(data_text)
    if save_path:
        img.save(save_path)
    return img


# converts image into qpixmap so pyqt label can display it
def pil_image_to_qpixmap(pil_img: Image.Image) -> QPixmap:
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    q_image = QImage()
    q_image.loadFromData(buffer.getvalue())
    return QPixmap.fromImage(q_image)
