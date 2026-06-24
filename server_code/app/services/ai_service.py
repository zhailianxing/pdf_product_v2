import json
import logging
import re
import time
from abc import ABC, abstractmethod
from pathlib import Path

import httpx

from app.config import get_settings
from app.schemas import AiExtractionResult, ChemicalItem, FieldItem, MechanicalItem
from app.services.pdf_utils import guess_supplier, pdf_to_base64_images

logger = logging.getLogger(__name__)

MAX_AI_LOG_CHARS = 4000

# 在材质报告里"几乎肯定只有上限（max）、Min 列必空"的化学项白名单。
# 用于 _build_extraction 的后处理"安全网"——纠正 VL 模型把 Max 行的值
# 错填到 min 的 row swap 错误（典型案例：Delta Ferrite 的 "1%" 被填到 min）。
#
# 选择标准（必须满足）：该元素/相在主流金属材质标准里物理意义上"越少越好"，
# 从来不会出现 Min 限值。
#
# 注意：C / S / P 不放进这里。表面看像"只有 max"的杂质元素，但在某些钢种里
# 它们是有 min 的：
#   - S：含 S 易切削不锈钢（1.4305 / 1.4435 / AISI 303 等）按 0.005–0.030 区间控制
#   - P：某些含 P 易切削钢、磷化处理钢
#   - C：某些高碳钢、铸钢
# 把它们放进白名单会误伤这些合法的"既有 min 又有 max"情况。
# 这些元素的 row swap 错误依靠 prompt + temperature=0 + DPI 提升来降低概率，
# 必要时由人工复核兜底。
_ONLY_MAX_CHEMICAL_ELEMENTS = {
    "delta ferrite", "delta-ferrite",
    "δ-ferrite", "δ ferrite", "δferrite",
    "δ-铁素体", "δ铁素体", "铁素体",
}


def _normalize_element_key(name: str) -> str:
    return (name or "").strip().lower().replace("  ", " ")


def _sanitize_chemical_min_max(item: dict) -> dict:
    """对化学成分单项做 min/max 一致性后处理，纠正 VL 模型常见的 row swap。

    触发翻转的两条规则（满足任一即翻转）：
      1) element 属于"只该有 max"白名单（如 Delta Ferrite / C / S / P），
         但模型给出 min 有值、max 为空 → 把 min 的值移到 max。
      2) min 是带 % 的数值且 max 为空（化学成分里带 % 的标准值默认是上限）
         → 把 min 的值移到 max。
    """
    elem_key = _normalize_element_key(item.get("element", ""))
    c_min = (item.get("min") or "").strip()
    c_max = (item.get("max") or "").strip()

    if not c_min or c_max:
        return item

    should_flip = False
    reason = ""
    if elem_key in _ONLY_MAX_CHEMICAL_ELEMENTS:
        should_flip = True
        reason = f"element={item.get('element')!r} 通常只有 max"
    elif c_min.rstrip().endswith("%"):
        should_flip = True
        reason = f"min={c_min!r} 带 %，化学成分里 % 默认是上限"

    if should_flip:
        logger.warning(
            "化学成分后处理修正: %s, 翻转 min=%r → max=%r (原 max=%r)",
            reason,
            c_min,
            c_min,
            c_max,
        )
        item["min"] = ""
        item["max"] = c_min
        if item.get("requirement"):
            item["requirement"] = ""

    return item

AUDIT_PROMPT = """你是金属材料材质报告（Material Certificate / EN10204 3.1）审核专家。
请分析材质报告图片，提取关键信息并判断化学成分和力学性能是否符合标准要求。

重要要求：
- min 表示下限（最小允许值），max 表示上限（最大允许值），两者含义不同，绝对不能填相同的值。
- min 和 max 必须严格按照报告表格中的 Min 行和 Max 行来填写，表格中该位置有值就填，没有值（空或 "－"）就填空字符串。
- actual、min、max 都必须从报告图片中实际读取，不要自行假设或编造。
- 力学性能中如果有多个屈服强度指标（如 Rp1.0 和 Rp0.2），必须作为独立的行分别列出，不要合并或遗漏。
- 报告中出现的每一项力学性能测试都必须列出，包括冲击值（Impact Value）等。

请严格返回 JSON（不要 markdown 代码块），格式如下：
{
  "ai_result": "PASS 或 FAIL",
  "reasons": ["失败原因列表，PASS 时可为空"],
  "supplier": "",
  "certificate_number": "",
  "material_grade": "",
  "standard": "",
  "heat_number": "",
  "batch_number": "",
  "date": "",
  "chemical_composition": "OK 或 FAIL",
  "mechanical_properties": "OK 或 FAIL",
  "fields": [{"label": "Supplier", "value": "..."}],
  "chemical": [
    {"element": "C", "actual": "<实测值>", "min": "", "max": "<上限>", "status": "ok"},
    {"element": "Cr", "actual": "<实测值>", "min": "<下限>", "max": "<上限>", "status": "ok"},
    {"element": "Delta Ferrite", "actual": "0.15%", "min": "", "max": "1%", "status": "ok"}
  ],
  "mechanical": [
    {"property": "Yield Strength Rp1.0", "actual": "<实测值>", "min": "<下限>", "max": "", "status": "ok"},
    {"property": "Yield Strength Rp0.2", "actual": "<实测值>", "min": "<下限>", "max": "", "status": "ok"},
    {"property": "Tensile Strength", "actual": "<实测值>", "min": "<下限>", "max": "<上限>", "status": "ok"},
    {"property": "Elongation A%", "actual": "<实测值>", "min": "<下限>", "max": "", "status": "ok"},
    {"property": "Hardness HB", "actual": "<实测值，如报告中为空或——则填空字符串>", "min": "", "max": "<上限，如报告中未给出则填空字符串>", "status": "ok"},
    {"property": "Impact Value", "actual": "<均值Mean value>", "min": "<下限，如60>", "max": "", "status": "ok"}
  ]
}

注意：
- C 只有 max 没有 min，Cr 有 min 和 max 范围。
- Yield Strength Rp1.0 和 Rp0.2 是两个独立的行，不要合并。
- 如果报告中某项实测值为空、——、或未填写，actual 必须填空字符串，不要编造数值。
- 如果报告中某项标准要求为空或未给出，min 和 max 也必须填空字符串。
- 请严格按此模式填写，不要把同一个值同时填入 min 和 max。

【化学成分 Min/Max 强约束 —— 必须严格遵守】
- 化学成分表通常是上下两行（Min 行 / Max 行）。读取时务必先在图像里
  逐列对齐确认：值是落在 "Min" 这一行（更靠上）还是 "Max" 这一行（更靠下）。
- 化学成分里**任何带百分号（%）的标准值默认是上限（max）**，不是下限。
  例如 Delta Ferrite 一格如果只看到一个 "1%" 或 "5%"，它一定是 max，
  对应的 min 必须填空字符串。
- Delta Ferrite / δ-Ferrite 这一项：在绝大多数欧标报告里 Min 列为空，
  Max 列才是上限（典型值 1%、3%、5%）。**永远不要把 Max 行里的 1% 误填到 min。**
- 注意：C / S / P 在不同钢种里 Min 列**可能有值也可能为空**——例如含 S 易切削
  不锈钢（如 EN 1.4435 / 1.4305 / AISI 303）的 S 会按 0.005–0.030 的区间控制，
  Min 行会真实出现一个数字。务必逐行肉眼对齐图像里 Min 行和 Max 行各自的格子，
  不要因为"印象里 S 总是杂质"就把 Max 行的值往 min 塞，也不要反过来漏填 max。
- 如果某一列只有一个孤立的数字（另一行完全空白），先确认它是写在 Min 行还是 Max 行，
  再决定填 min 还是 max；不要因为"只有一个值"就默认填 min。
"""


def _build_extraction(data: dict, file_name: str) -> tuple[str, AiExtractionResult, list[str]]:
    ai_result = str(data.get("ai_result", "FAIL")).upper()
    if ai_result not in ("PASS", "FAIL"):
        ai_result = "FAIL"
    reasons = data.get("reasons") or []
    supplier = data.get("supplier") or guess_supplier(file_name)

    fields_raw = data.get("fields") or []
    fields = [FieldItem(**f) if isinstance(f, dict) else f for f in fields_raw]
    if not fields:
        fields = [
            FieldItem(label="Supplier", value=supplier),
            FieldItem(label="Certificate Number", value=data.get("certificate_number", "")),
            FieldItem(label="Material Grade", value=data.get("material_grade", "")),
            FieldItem(label="Standard", value=data.get("standard", "")),
            FieldItem(
                label="Heat Number",
                value=data.get("heat_number", "—"),
                highlight=not data.get("heat_number") or data.get("heat_number") == "—",
            ),
            FieldItem(label="Batch / Lot Number", value=data.get("batch_number", "")),
            FieldItem(label="Date", value=data.get("date", "")),
        ]

    chemical_raw = data.get("chemical") or []
    chemical = []
    for c in chemical_raw:
        if isinstance(c, dict):
            c = _sanitize_chemical_min_max(c)
            c_min = c.get("min", "")
            c_max = c.get("max", "")
            if not c.get("requirement"):
                if c_min and c_max:
                    c["requirement"] = f"{c_min}–{c_max}"
                elif c_max:
                    c["requirement"] = f"≤{c_max}"
                elif c_min:
                    c["requirement"] = f"≥{c_min}"
                else:
                    c["requirement"] = ""
            chemical.append(ChemicalItem(**c))
        else:
            chemical.append(c)
    mechanical_raw = data.get("mechanical") or []
    mechanical = []
    for m in mechanical_raw:
        if isinstance(m, dict):
            m_min = m.get("min", "")
            m_max = m.get("max", "")
            if not m.get("requirement"):
                if m_min and m_max:
                    m["requirement"] = f"{m_min}–{m_max}"
                elif m_max:
                    m["requirement"] = f"≤{m_max}"
                elif m_min:
                    m["requirement"] = f"≥{m_min}"
                else:
                    m["requirement"] = ""
            mechanical.append(MechanicalItem(**m))
        else:
            mechanical.append(m)

    extraction = AiExtractionResult(
        materialGrade=data.get("material_grade", ""),
        heatNumber=data.get("heat_number", "—"),
        supplier=supplier,
        certificateNumber=data.get("certificate_number", ""),
        standard=data.get("standard", ""),
        batchNumber=data.get("batch_number", ""),
        date=data.get("date", ""),
        chemicalComposition=data.get("chemical_composition", "OK"),
        mechanicalProperties=data.get("mechanical_properties", "OK"),
        fields=fields,
        chemical=chemical,
        mechanical=mechanical,
        reasons=reasons,
    )
    return ai_result, extraction, reasons


def _truncate_for_log(text: str, max_chars: int = MAX_AI_LOG_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return f"{text[:max_chars]}...<truncated {len(text) - max_chars} chars>"


def _try_parse_json(text: str) -> dict:
    """Try to parse JSON, attempting repair for truncated AI responses."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    repaired = text
    # Close any unterminated string
    open_quotes = repaired.count('"') % 2
    if open_quotes:
        repaired += '"'
    # Balance brackets/braces
    open_braces = repaired.count("{") - repaired.count("}")
    open_brackets = repaired.count("[") - repaired.count("]")
    repaired += "]" * max(open_brackets, 0)
    repaired += "}" * max(open_braces, 0)

    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # Last resort: find the outermost { ... } and try to parse that
    match = re.search(r"\{", text)
    if match:
        depth = 0
        last_close = -1
        for i, ch in enumerate(text):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                last_close = i
        if last_close > 0:
            candidate = text[match.start() : last_close + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

    raise ValueError(
        f"AI 模型返回的 JSON 无法解析且修复失败，原始内容前 500 字符: {text[:500]}"
    )


class BaseAiClient(ABC):
    @abstractmethod
    async def audit_pdf(self, pdf_path: Path, file_name: str) -> tuple[str, AiExtractionResult, list[str], str, float]:
        """返回 (ai_result, extraction, reasons, model_name, process_time_ms)"""


class MockAiClient(BaseAiClient):
    async def audit_pdf(self, pdf_path: Path, file_name: str) -> tuple[str, AiExtractionResult, list[str], str, float]:
        start = time.perf_counter()
        supplier = guess_supplier(file_name)
        fail_keywords = ["博坦", "巨力", "轩诺"]
        ai_result = "FAIL" if any(k in file_name for k in fail_keywords) else "PASS"

        if ai_result == "PASS":
            data = {
                "ai_result": "PASS",
                "reasons": [],
                "supplier": supplier if supplier != "未知厂商" else "VDV Metal Co.",
                "certificate_number": "MC-2026-004521",
                "material_grade": "ASTM A182 F316L",
                "standard": "EN 10204 3.1",
                "heat_number": "A123456",
                "batch_number": "LOT-20260528",
                "date": "2026-05-28",
                "chemical_composition": "OK",
                "mechanical_properties": "OK",
                "chemical": [
                    {"element": "C", "actual": "0.018", "min": "", "max": "0.030", "status": "ok"},
                    {"element": "S", "actual": "0.008", "min": "", "max": "0.030", "status": "ok"},
                ],
                "mechanical": [
                    {"property": "Yield Strength", "actual": "245 MPa", "requirement": "≥170 MPa", "status": "ok"},
                    {"property": "Tensile Strength", "actual": "520 MPa", "requirement": "≥485 MPa", "status": "ok"},
                ],
            }
        else:
            data = {
                "ai_result": "FAIL",
                "reasons": [
                    "炉号 (Heat Number) 缺失或无法可靠识别",
                    "S元素（硫）化学成分超出预设标准范围",
                ],
                "supplier": supplier if supplier != "未知厂商" else "博坦 Steel",
                "certificate_number": "BT-2026-00891",
                "material_grade": "ASTM A182 F316L",
                "standard": "EN 10204 3.1",
                "heat_number": "—",
                "batch_number": "LOT-20260530",
                "date": "2026-05-30",
                "chemical_composition": "FAIL",
                "mechanical_properties": "OK",
                "chemical": [
                    {"element": "S", "actual": "0.042", "min": "", "max": "0.030", "status": "fail"},
                ],
                "mechanical": [
                    {"property": "Tensile Strength", "actual": "495 MPa", "requirement": "≥485 MPa", "status": "ok"},
                ],
            }

        result, extraction, reasons = _build_extraction(data, file_name)
        elapsed = (time.perf_counter() - start) * 1000
        return result, extraction, reasons, "mock", elapsed


async def _audit_with_vision_api(
    pdf_path: Path,
    file_name: str,
    *,
    base_url: str,
    api_key: str,
    model: str,
    timeout: int,
    request_options: dict | None = None,
) -> tuple[str, AiExtractionResult, list[str], str, float]:
    start = time.perf_counter()
    images = pdf_to_base64_images(pdf_path)
    if not images:
        raise ValueError("无法读取 PDF 内容")

    content: list[dict] = [{"type": "text", "text": AUDIT_PROMPT}]
    for img_b64 in images:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_b64}"},
            }
        )

    payload: dict = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
    }
    if request_options:
        payload.update(request_options)

    endpoint = f"{base_url.rstrip('/')}/chat/completions"
    logger.info(
        "开始调用视觉模型 model=%s endpoint=%s file=%s image_count=%s timeout=%ss",
        model,
        endpoint,
        file_name,
        len(images),
        timeout,
    )

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except httpx.HTTPError as exc:
        elapsed = (time.perf_counter() - start) * 1000
        logger.exception(
            "视觉模型请求异常 model=%s endpoint=%s elapsed_ms=%.2f error=%s",
            model,
            endpoint,
            elapsed,
            exc,
        )
        raise

    elapsed = (time.perf_counter() - start) * 1000
    raw_response = response.text
    logger.info(
        "视觉模型返回 status=%s model=%s elapsed_ms=%.2f body=%s",
        response.status_code,
        model,
        elapsed,
        _truncate_for_log(raw_response),
    )

    if response.is_error:
        logger.error(
            "视觉模型调用失败 status=%s model=%s elapsed_ms=%.2f body=%s",
            response.status_code,
            model,
            elapsed,
            _truncate_for_log(raw_response),
        )
        response.raise_for_status()

    try:
        body = response.json()
    except ValueError:
        logger.exception(
            "视觉模型返回非 JSON model=%s elapsed_ms=%.2f body=%s",
            model,
            elapsed,
            _truncate_for_log(raw_response),
        )
        raise

    text = body["choices"][0]["message"]["content"]
    text = text.strip()
    logger.info(
        "视觉模型消息内容 model=%s elapsed_ms=%.2f content=%s",
        model,
        elapsed,
        _truncate_for_log(text),
    )
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    try:
        data = _try_parse_json(text)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error(
            "视觉模型返回 JSON 解析失败 model=%s error=%s content=%s",
            model,
            exc,
            _truncate_for_log(text),
        )
        raise ValueError(f"AI 模型返回的内容不是合法 JSON: {exc}") from exc

    result, extraction, reasons = _build_extraction(data, file_name)
    elapsed = (time.perf_counter() - start) * 1000
    return result, extraction, reasons, model, elapsed


class KimiAiClient(BaseAiClient):
    async def audit_pdf(self, pdf_path: Path, file_name: str) -> tuple[str, AiExtractionResult, list[str], str, float]:
        settings = get_settings()
        if not settings.moonshot_api_key:
            logger.warning("MOONSHOT_API_KEY 未配置，降级为 mock 模式")
            return await MockAiClient().audit_pdf(pdf_path, file_name)

        return await _audit_with_vision_api(
            pdf_path,
            file_name,
            base_url=settings.moonshot_base_url,
            api_key=settings.moonshot_api_key,
            model=settings.kimi_model,
            timeout=settings.ai_request_timeout,
            # kimi-k2.5 仅允许 temperature=1；关闭 thinking 以加快 JSON 审核响应
            request_options={"thinking": {"type": "disabled"}},
        )


class LocalAiClient(BaseAiClient):
    """本地 OpenAI 兼容视觉模型（Ollama / vLLM 等，如 Qwen3-VL）。"""

    async def audit_pdf(self, pdf_path: Path, file_name: str) -> tuple[str, AiExtractionResult, list[str], str, float]:
        settings = get_settings()
        # 关掉随机采样并固定 seed，避免对同一张 PDF 的相同输入产生不同的 min/max 抽取结果
        # （Qwen3-VL 在窄列模糊单元格上很容易 row swap，例如 Delta Ferrite 的 Min 空 / Max=1%）
        return await _audit_with_vision_api(
            pdf_path,
            file_name,
            base_url=settings.local_base_url,
            api_key=settings.local_api_key,
            model=settings.local_model,
            timeout=settings.ai_request_timeout,
            request_options={
                "temperature": 0.0,
                "top_p": 1.0,
                "seed": 42,
                "max_tokens": 4096,
            },
        )


def get_ai_client() -> BaseAiClient:
    settings = get_settings()
    provider = settings.ai_provider.lower()
    if provider == "mock":
        return MockAiClient()
    if provider == "local":
        return LocalAiClient()
    if provider == "kimi":
        return KimiAiClient()
    return MockAiClient()
