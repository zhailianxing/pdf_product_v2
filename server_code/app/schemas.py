from datetime import datetime
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: T | None = None


class LoginRequest(BaseModel):
    username: str
    password: str = ""
    role: Literal["admin", "auditor"] = "auditor"


class UserInfo(BaseModel):
    id: int
    username: str
    name: str
    role: str
    status: str
    last_login: datetime | None = None

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    token: str
    user: UserInfo


class RecordListItem(BaseModel):
    id: str
    fileName: str
    supplier: str
    uploader: str
    uploadTime: str
    aiResult: str
    manualResult: str | None = None
    adminSpotCheckResult: str | None = None


class FieldItem(BaseModel):
    label: str
    value: str
    highlight: bool = False


class ChemicalItem(BaseModel):
    element: str
    actual: str
    min: str = ""
    max: str = ""
    requirement: str = ""
    status: str


class MechanicalItem(BaseModel):
    model_config = {"protected_namespaces": ()}

    property: str
    actual: str
    min: str = ""
    max: str = ""
    requirement: str = ""
    status: str


class AiExtractionResult(BaseModel):
    materialGrade: str = ""
    heatNumber: str = ""
    supplier: str = ""
    certificateNumber: str = ""
    standard: str = ""
    batchNumber: str = ""
    date: str = ""
    chemicalComposition: str = "OK"
    mechanicalProperties: str = "OK"
    fields: list[FieldItem] = Field(default_factory=list)
    chemical: list[ChemicalItem] = Field(default_factory=list)
    mechanical: list[MechanicalItem] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


class RecordDetail(RecordListItem):
    aiDetail: AiExtractionResult | None = None
    aiReasons: list[str] = Field(default_factory=list)
    comment: str | None = None
    modelName: str = ""
    processTimeMs: float | None = None
    pdfUrl: str = ""


class WorkspaceResponse(BaseModel):
    record: RecordDetail
    aiStatus: Literal["pass", "fail"]


class ManualReviewRequest(BaseModel):
    action: Literal["confirm_fail", "override_pass"]
    comment: str | None = None


class CommentRequest(BaseModel):
    comment: str


class SpotCheckRequest(BaseModel):
    result: Literal["PASS", "FAIL"]
    comment: str | None = None


class AuditLogItem(BaseModel):
    id: str
    time: str
    action: str
    recordId: str | None = None
    fileName: str | None = None
    operator: str
    detail: str
    result: str | None = None


class AuditLogStats(BaseModel):
    total: int
    upload: int
    aiAudit: int
    manual: int
    spotCheck: int


class AuditLogListResponse(BaseModel):
    items: list[AuditLogItem]
    stats: AuditLogStats


class KpiData(BaseModel):
    totalReports: int
    passRate: float
    failRate: float
    avgProcessTime: float
    trends: dict[str, str]


class PendingQueueItem(BaseModel):
    id: str
    fileName: str
    supplier: str
    reason: str
    uploadTime: str


class DashboardResponse(BaseModel):
    kpi: KpiData
    pendingQueue: list[PendingQueueItem]
