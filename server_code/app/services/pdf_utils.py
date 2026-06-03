import base64
import io
from pathlib import Path

import fitz


def pdf_to_base64_images(pdf_path: str | Path, max_pages: int = 3, dpi: int = 150) -> list[str]:
    """将 PDF 前几页转为 base64 PNG，供视觉模型使用。"""
    images: list[str] = []
    doc = fitz.open(str(pdf_path))
    try:
        for page_index in range(min(len(doc), max_pages)):
            page = doc.load_page(page_index)
            pix = page.get_pixmap(dpi=dpi)
            images.append(base64.b64encode(pix.tobytes("png")).decode("utf-8"))
    finally:
        doc.close()
    return images


def guess_supplier(file_name: str) -> str:
    suppliers = ["博坦", "轩诺", "VDV", "威地威", "迪宝", "巨力", "高纬", "R470"]
    for name in suppliers:
        if name in file_name:
            if name == "威地威":
                return "VDV"
            return name
    return "未知厂商"
