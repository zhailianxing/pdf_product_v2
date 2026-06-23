import re

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


_CHEMICAL_ELEMENTS = {"C", "Si", "Mn", "P", "S", "Cr", "Mo", "Ni", "Ti", "N", "Cu", "Al", "V", "Nb", "CE", "W", "Co", "B"}

_CHEM_LINE_RE = re.compile(
    r"^(Min|Max)\s+[－—\-\d]"
    r"|^C\s+Si\s+Mn\s+"
    r"|^\d+\s+\d{5,}\s+\w+\s+\d+\.\d+"
)


def _normalize_cell(cell) -> str:
    if cell is None:
        return ""
    return str(cell).replace("\n", " ").strip()


def _find_row_by_label(rows: list[list[str]], label: str) -> list[str] | None:
    for row in rows:
        for cell in row:
            if cell.strip().lower() == label.lower():
                return row
    return None


def _extract_chemical_data(tables: list[list[list]]) -> str | None:
    """从 pdfplumber 表格中提取化学成分，转为每元素一行的竖排格式。"""
    for raw_table in tables:
        rows = [[_normalize_cell(c) for c in row] for row in raw_table]

        header_row = None
        header_idx = -1
        for i, row in enumerate(rows):
            element_count = sum(1 for c in row if c in _CHEMICAL_ELEMENTS)
            if element_count >= 4:
                header_row = row
                header_idx = i
                break

        if not header_row:
            continue

        min_row = _find_row_by_label(rows[header_idx + 1:], "Min")
        max_row = _find_row_by_label(rows[header_idx + 1:], "Max")

        data_rows = []
        for row in rows[header_idx + 1:]:
            first_cell = row[0].strip() if row[0] else ""
            if first_cell and first_cell[0].isdigit() and first_cell not in ("1%", "0.15%"):
                data_rows.append(row)

        if not min_row and not max_row:
            continue

        elem_start = -1
        for j, cell in enumerate(header_row):
            if cell in _CHEMICAL_ELEMENTS:
                elem_start = j
                break

        if elem_start < 0:
            continue

        elem_cols: list[tuple[str, int]] = []
        for j in range(elem_start, len(header_row)):
            cell = header_row[j]
            if cell in _CHEMICAL_ELEMENTS:
                elem_cols.append((cell, j))
            elif cell and cell not in ("", "Delta Ferrite") and "Coupon" in cell:
                break

        def _get(row: list[str] | None, idx: int) -> str:
            if row is None or idx >= len(row):
                return ""
            v = row[idx].strip()
            if v in ("－", "—", "—", "-", "–"):
                return ""
            return v

        lines = ["=== 化学成分（已从表格预处理，请直接使用）==="]
        for elem, j in elem_cols:
            min_val = _get(min_row, j)
            max_val = _get(max_row, j)
            actual_val = _get(data_rows[0], j) if data_rows else ""
            lines.append(f"{elem}: Min={min_val or '无'}, Max={max_val or '无'}, Actual={actual_val}")

        delta_idx = None
        for j, cell in enumerate(header_row):
            if "Delta" in cell or "Ferrite" in cell:
                delta_idx = j
                break
        if delta_idx is not None:
            lines.append(f"Delta Ferrite: Min={_get(min_row, delta_idx) or '无'}, Max={_get(max_row, delta_idx) or '无'}, Actual={_get(data_rows[0], delta_idx) if data_rows else ''}")

        return "\n".join(lines)

    return None


def _strip_chemical_lines(text: str) -> str:
    """从页面文本中移除化学成分相关的行（Min/Max 数据行、元素表头行、数据行）。"""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if _CHEM_LINE_RE.match(stripped):
            continue
        if stripped in ("1 2 3", "value", "Mean"):
            continue
        cleaned.append(stripped)
    return "\n".join(cleaned)


def pdf_to_text_and_tables(pdf_path: str | Path, max_pages: int = 3) -> str:
    """用 pdfplumber 提取 PDF，化学成分做列对齐转竖排，其余用清理后的文本。"""
    sections: list[str] = []

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_index in range(min(len(pdf.pages), max_pages)):
            page = pdf.pages[page_index]

            chem_data = None
            tables = page.extract_tables()
            if tables:
                chem_data = _extract_chemical_data(tables)

            text = page.extract_text() or ""

            if chem_data:
                sections.append(chem_data)
                text = _strip_chemical_lines(text)

            if text.strip():
                sections.append(text.strip())

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
