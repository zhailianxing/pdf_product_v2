# 材质报告 AI 自动审核系统 — 服务端

Python + FastAPI 实现，对接 `front_code/web-admin` 后台管理系统。

## 快速启动

```bash
cd server_code
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
copy .env.example .env

# 初始化 MySQL 数据库（建表 + mock 数据）
python init_database.py --reset

python run.py
```

服务默认运行在 http://127.0.0.1:8080  
API 文档：http://127.0.0.1:8080/docs

## 数据库（MySQL）

默认连接本地 MySQL 数据库 `pdf_vl`：

```env
DATABASE_URL=mysql+pymysql://root:123456@localhost:3306/pdf_vl?charset=utf8mb4
```

初始化建表并导入 mock 数据：

```bash
python init_database.py          # 空库时写入 mock
python init_database.py --reset  # 清空后重新导入
```

表结构：`users`、`upload_records`、`audit_logs`

## 演示账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| auditor01 | 123456 | 审核员 |

## AI 模型配置

默认 `AI_PROVIDER=kimi`，调用 Moonshot/Kimi 视觉模型（可配置为 `kimi-k2.5` 等）。

未配置 `MOONSHOT_API_KEY` 时自动降级为 **mock 模式**（按文件名规则模拟 PASS/FAIL）。

```env
AI_PROVIDER=kimi          # kimi | mock | local
MOONSHOT_API_KEY=sk-xxx
KIMI_MODEL=kimi-k2.5
```

切换本地 Qwen3-VL（Ollama 等）：

```env
AI_PROVIDER=local
LOCAL_BASE_URL=http://localhost:11434/v1
LOCAL_API_KEY=ollama
LOCAL_MODEL=qwen3-vl:8b
```

## 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 登录 |
| GET | `/api/v1/auth/me` | 当前用户 |
| POST | `/api/v1/records/upload` | 上传 PDF + AI 审核 |
| GET | `/api/v1/records` | 上传记录列表 |
| GET | `/api/v1/records/{id}` | 记录详情 |
| GET | `/api/v1/records/{id}/workspace` | AI 审核工作台数据 |
| GET | `/api/v1/records/{id}/file` | 下载/预览 PDF |
| POST | `/api/v1/records/{id}/manual-review` | 人工确认 FAIL / 强转 PASS |
| POST | `/api/v1/records/{id}/comment` | 添加审核备注 |
| POST | `/api/v1/records/{id}/spot-check` | 管理员抽检（需 admin） |
| GET | `/api/v1/audit-logs` | 审核日志列表 |
| GET | `/api/v1/dashboard` | 仪表盘 KPI + 待审核队列 |
| GET | `/api/v1/users` | 用户列表（需 admin） |

请求头：`Authorization: Bearer <token>`

统一响应格式：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

## 目录结构

```
server_code/
  app/
    main.py           # FastAPI 入口
    models.py         # 数据库模型
    routers/          # API 路由
    services/         # 业务逻辑 + AI 调用
  uploads/            # 上传 PDF 存储
  data/               # SQLite 数据库
```

启动时会自动初始化数据库，并从 `mock_data/` 导入示例 PDF 记录。
