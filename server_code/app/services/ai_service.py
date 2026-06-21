import json
import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path

import httpx

from app.config import get_settings
from app.schemas import AiExtractionResult, ChemicalItem, FieldItem, MechanicalItem
from app.services.pdf_utils import guess_supplier, pdf_to_base64_images

logger = logging.getLogger(__name__)

MAX_AI_LOG_CHARS = 4000

AUDIT_PROMPT = """你是金属材料材质报告（Material Certificate / EN10204 3.1）审核专家。
请分析材质报告图片，提取关键信息并判断化学成分和力学性能是否符合标准要求。

重要要求：
- min 表示下限（最小允许值），max 表示上限（最大允许值），请勿混淆。
- 化学成分：报告中的标准要求绝大多数是上限（max），例如 "C: 0.07" 或 "C max 0.07" 表示碳含量不得超过 0.07，应填 max="0.07", min=""。只有少数元素（如 Cr、Ni、Mo）会给出范围（如 "16.0-18.0"），此时 min="16.0", max="18.0"。
- 力学性能：Yield Strength、Tensile Strength、Elongation 等通常给的是下限（min），如 "min. 30" 表示不得低于 30，应填 min="30", max=""。Hardness 通常给的是上限（max）。
- actual、min、max 都必须从报告图片中实际读取，不要自行假设或使用通用标准值。
- 如果某项只有 min 没有 max，则 max 填空字符串，反之亦然。

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
  "chemical": [{"element": "<元素符号>", "actual": "<报告中的实测值>", "min": "<下限，无则为空>", "max": "<上限，无则为空>", "status": "ok 或 fail"}],
  "mechanical": [{"property": "<性能名称>", "actual": "<报告中的实测值>", "min": "<下限，无则为空>", "max": "<上限，无则为空>", "status": "ok 或 fail"}]
}
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

    data = json.loads(text)
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
        return await _audit_with_vision_api(
            pdf_path,
            file_name,
            base_url=settings.local_base_url,
            api_key=settings.local_api_key,
            model=settings.local_model,
            timeout=settings.ai_request_timeout,
            request_options={"temperature": 0.1},
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
