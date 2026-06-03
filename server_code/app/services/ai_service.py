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

AUDIT_PROMPT = """你是金属材料材质报告（Material Certificate / EN10204 3.1）审核专家。
请分析材质报告图片，提取关键信息并判断化学成分和力学性能是否符合标准要求。

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
  "chemical": [{"element": "C", "actual": "0.018", "requirement": "≤0.030", "status": "ok"}],
  "mechanical": [{"property": "Yield Strength", "actual": "245 MPa", "requirement": "≥170 MPa", "status": "ok"}]
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

    chemical = [
        ChemicalItem(**c) if isinstance(c, dict) else c for c in (data.get("chemical") or [])
    ]
    mechanical = [
        MechanicalItem(**m) if isinstance(m, dict) else m for m in (data.get("mechanical") or [])
    ]

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
                    {"element": "C", "actual": "0.018", "requirement": "≤0.030", "status": "ok"},
                    {"element": "S", "actual": "0.008", "requirement": "≤0.030", "status": "ok"},
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
                    {"element": "S", "actual": "0.042", "requirement": "≤0.030", "status": "fail"},
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

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        if response.is_error:
            logger.error(
                "视觉模型调用失败 status=%s model=%s body=%s",
                response.status_code,
                model,
                response.text[:1000],
            )
            response.raise_for_status()
        body = response.json()

    text = body["choices"][0]["message"]["content"]
    text = text.strip()
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
