import re
import base64
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


_CHEMICAL_ELEMENTS = {
    "C", "Si", "Mn", "P", "S", "Cr", "Mo", "Ni", "Ti", "N",
    "Cu", "Al", "V", "Nb", "CE", "W", "Co", "B",
}

_DASH_CHARS = {"－", "—", "—", "-", "–", "——"}


def _normalize_cell(cell) -> str:
    if cell is None:
        return ""
    return str(cell).replace("\n", " ").strip()


def _is_dash(val: str) -> bool:
    return val.strip() in _DASH_CHARS or val.strip() == ""


def _get_cell(row: list[str] | None, idx: int) -> str:
    if row is None or idx >= len(row):
        return ""
    v = row[idx].strip()
    if v in _DASH_CHARS:
        return ""
    return v


def _parse_number(text: str) -> str:
    """从文本中提取数字，如 'Min. 205' -> '205', 'min.25' -> '25', 'Min.50J' -> '50'."""
    m = re.search(r"(\d+\.?\d*)", text)
    return m.group(1) if m else ""


def _parse_range(text: str) -> tuple[str, str]:
    """从文本中提取范围，如 '390-640' -> ('390', '640')."""
    m = re.search(r"(\d+\.?\d*)\s*[-–—]\s*(\d+\.?\d*)", text)
    if m:
        return m.group(1), m.group(2)
    return "", ""


def _find_row_by_label(rows: list[list[str]], label: str) -> list[str] | None:
    for row in rows:
        for cell in row:
            if cell.strip().lower() == label.lower():
                return row
    return None


def _extract_all_table_data(tables: list[list[list]]) -> str | None:
    """从 pdfplumber 表格中提取化学成分和力学性能，转为竖排格式。"""
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

        data_row = data_rows[0] if data_rows else None
        num_cols = len(header_row)

        # === 化学成分提取 ===
        elem_start = -1
        for j, cell in enumerate(header_row):
            if cell in _CHEMICAL_ELEMENTS:
                elem_start = j
                break

        if elem_start < 0:
            continue

        elem_cols: list[tuple[str, int]] = []
        mech_start = num_cols
        for j in range(elem_start, num_cols):
            cell = header_row[j]
            if cell in _CHEMICAL_ELEMENTS:
                elem_cols.append((cell, j))
            elif "Delta" in cell or "Ferrite" in cell:
                elem_cols.append(("Delta Ferrite", j))
            elif cell and ("Coupon" in cell or "Tensile" in cell or "strength" in cell.lower()):
                mech_start = j
                break

        lines = ["=== 化学成分（已从表格预处理，请直接使用）==="]
        for elem, j in elem_cols:
            min_val = _get_cell(min_row, j)
            max_val = _get_cell(max_row, j)
            actual_val = _get_cell(data_row, j)
            lines.append(f"{elem}: Min={min_val or '无'}, Max={max_val or '无'}, Actual={actual_val}")

        # === 力学性能提取 ===
        sub_header_row = None
        for row in rows[header_idx + 1:]:
            has_rp = any("Rp" in cell or "rp" in cell for cell in row if cell)
            if has_rp:
                sub_header_row = row
                break

        mech_lines = ["", "=== 力学性能（已从表格预处理，请直接使用）==="]

        for j in range(mech_start, num_cols):
            h_cell = header_row[j] if j < len(header_row) else ""
            sub_cell = _normalize_cell(sub_header_row[j]) if sub_header_row and j < len(sub_header_row) else ""
            min_cell = _get_cell(min_row, j)
            actual_cell = _get_cell(data_row, j)

            if not h_cell and not sub_cell:
                continue

            if "Coupon" in h_cell:
                continue

            if "Tensile" in h_cell or "tensile" in h_cell.lower():
                t_min, t_max = _parse_range(h_cell)
                mech_lines.append(f"Tensile Strength: Min={t_min or '无'}, Max={t_max or '无'}, Actual={actual_cell}")

            elif ("Submit" in h_cell or "strength" in h_cell.lower() or "Rp" in sub_cell):
                if "Rp1" in sub_cell or "Rp1" in h_cell:
                    rp_min = _parse_number(min_cell) if min_cell else ""
                    mech_lines.append(f"Yield Strength Rp1.0: Min={rp_min or '无'}, Max=无, Actual={actual_cell}")
                elif "Rp0" in sub_cell or "Rp0" in h_cell:
                    rp_min = _parse_number(min_cell) if min_cell else ""
                    mech_lines.append(f"Yield Strength Rp0.2: Min={rp_min or '无'}, Max=无, Actual={actual_cell}")

            elif "Extension" in h_cell or "Elongation" in h_cell:
                ext_min = _parse_number(h_cell)
                mech_lines.append(f"Elongation A%: Min={ext_min or '无'}, Max=无, Actual={actual_cell}")

            elif "Hardness" in h_cell:
                hard_max = _parse_number(h_cell) if re.search(r"\d", h_cell.replace("HB", "")) else ""
                mech_lines.append(f"Hardness HB: Min=无, Max={hard_max or '无'}, Actual={actual_cell}")

        impact_header = ""
        for j in range(mech_start, num_cols):
            sub_cell = _normalize_cell(sub_header_row[j]) if sub_header_row and j < len(sub_header_row) else ""
            h_above = ""
            for check_row in rows[max(0, header_idx - 2):header_idx + 2]:
                for cell in check_row:
                    if "impact" in cell.lower() or "Impact" in cell:
                        h_above = cell
                        break
            if "impact" in sub_cell.lower() or "Min." in sub_cell:
                impact_header = sub_cell
                break
            if h_above and not impact_header:
                impact_header = h_above

        impact_min = ""
        if impact_header:
            impact_min = _parse_number(impact_header)

        mean_col = None
        if min_row:
            for j in range(mech_start, num_cols):
                cell = _get_cell(min_row, j)
                if "Mean" in cell or "mean" in cell:
                    mean_col = j
                    break

        if mean_col is not None and data_row:
            impact_actual = _get_cell(data_row, mean_col)
            mech_lines.append(f"Impact Value: Min={impact_min or '无'}, Max=无, Actual={impact_actual}")
        elif impact_header:
            last_actual = ""
            if data_row:
                for j in range(num_cols - 1, mech_start, -1):
                    v = _get_cell(data_row, j)
                    if v and re.match(r"\d+\.?\d*$", v):
                        last_actual = v
                        break
            mech_lines.append(f"Impact Value: Min={impact_min or '无'}, Max=无, Actual={last_actual}")

        lines.extend(mech_lines)
        return "\n".join(lines)

    return None


_TABLE_DATA_LINE_RE = re.compile(
    r"^(Min|Max)\s+[－—\-\d]"
    r"|^C\s+Si\s+Mn\s+"
    r"|^\d+\s+\d{5,}\s+\w+\s+\d+\.\d+"
    r"|^(Coupon|Tensile|Submit|Extension|Hardness|Mechnical|Chemical)"
    r"|^(EN\s+ISO|impact\s+value|acc\.\s+to)"
    r"|^(Rp1|Rp0|Delta)"
    r"|^(390-640|min\.\s*\d+|Min\.\s*\d+)"
    r"|^\d+$"
)


def _strip_table_lines(text: str) -> str:
    """从页面文本中移除表格相关的行。"""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if _TABLE_DATA_LINE_RE.match(stripped):
            continue
        if stripped in ("1 2 3", "value", "Mean", "%", "Pos. ITEM No. Heat No."):
            continue
        cleaned.append(stripped)
    return "\n".join(cleaned)


def pdf_to_text_and_tables(pdf_path: str | Path, max_pages: int = 3) -> str:
    """用 pdfplumber 提取 PDF，化学+力学做列对齐转竖排，其余用清理后的文本。"""
    sections: list[str] = []

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_index in range(min(len(pdf.pages), max_pages)):
            page = pdf.pages[page_index]

            table_data = None
            tables = page.extract_tables()
            if tables:
                table_data = _extract_all_table_data(tables)

            text = page.extract_text() or ""

            if table_data:
                sections.append(table_data)
                text = _strip_table_lines(text)

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
