import base64
import io
from pathlib import Path

import fitz


def pdf_to_base64_images(pdf_path: str | Path, max_pages: int = 3, dpi: int = 220) -> list[str]:
    """将 PDF 前几页转为 base64 PNG，供视觉模型使用。

    DPI 220 是 A4 横版材质报告在 Qwen3-VL 上的清晰度/速度甜点：
    比 150 提升约 2× 像素密度，可以让 Delta Ferrite 这种窄列里的
    "1%" 和空白单元格在 vision tokens 里区分得更明确，显著降低
    行错位（min/max 互换）的概率。再高（300+）反而会触发 Qwen-VL
    的 patch 上限和速度下降。
    """
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
