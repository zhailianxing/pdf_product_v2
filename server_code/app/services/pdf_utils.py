import base64
import io
import logging
from pathlib import Path

import fitz
import pdfplumber

logger = logging.getLogger(__name__)


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


def _clean_table(table: list[list[str | None]]) -> list[list[str]]:
    """去掉完全空的行和列，合并多行文本。"""
    if not table:
        return []
    cleaned = []
    for row in table:
        cells = [str(cell).replace("\n", " ").strip() if cell else "" for cell in row]
        cleaned.append(cells)

    if not cleaned:
        return []

    num_cols = len(cleaned[0])
    non_empty_cols = [
        j for j in range(num_cols)
        if any(cleaned[i][j] for i in range(len(cleaned)))
    ]
    cleaned = [[row[j] for j in non_empty_cols] for row in cleaned]

    result = [row for row in cleaned if any(cell for cell in row)]
    return result


def _table_to_markdown(table: list[list[str]]) -> str:
    """将清理后的表格转为 Markdown 格式。"""
    if not table:
        return ""
    rows = []
    for row in table:
        rows.append("| " + " | ".join(row) + " |")
        if len(rows) == 1:
            rows.append("| " + " | ".join(["---"] * len(row)) + " |")
    return "\n".join(rows)


def pdf_to_text_and_tables(pdf_path: str | Path, max_pages: int = 3) -> str:
    """用 pdfplumber 提取 PDF 的文本，返回紧凑的纯文本内容。"""
    sections: list[str] = []

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_index in range(min(len(pdf.pages), max_pages)):
            page = pdf.pages[page_index]
            text = page.extract_text()
            if text:
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                sections.append("\n".join(lines))

    result = "\n\n".join(sections)
    logger.info("PDF 文本提取完成 file=%s chars=%d", pdf_path, len(result))
    return result


def guess_supplier(file_name: str) -> str:
    suppliers = ["博坦", "轩诺", "VDV", "威地威", "迪宝", "巨力", "高纬", "R470"]
    for name in suppliers:
        if name in file_name:
            if name == "威地威":
                return "VDV"
            return name
    return "未知厂商"
