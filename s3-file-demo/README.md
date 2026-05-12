# S3 File Upload/Download Demo

一个基于 FastAPI + SQLite + S3（支持 MinIO）的最小可运行 Demo：

- 支持**多文件上传**（一次接口可上传多个文件）
- 支持**单文件下载**（通过文件 ID）
- 使用 SQLite 记录文件元数据：保留**原始文件名** + **S3 存储名**（UUID，确保 S3 不重名）
- 文件实体存储到 S3 / MinIO

## 目录结构

```
s3-file-demo/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI 入口
│   ├── config.py         # 配置（env）
│   ├── database.py       # SQLAlchemy 引擎/Session
│   ├── models.py         # FileRecord 表
│   ├── schemas.py        # Pydantic 模型
│   ├── s3_client.py      # S3/MinIO 封装
│   └── routers/
│       ├── __init__.py
│       └── files.py      # upload / download 路由
├── requirements.txt
├── .env.example
└── README.md
```

## 安装

```powershell
cd s3-file-demo
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # 然后按需修改
```

## 启动 MinIO（本地开发，可选）

```powershell
docker run -d --name minio -p 9000:9000 -p 9001:9001 `
  -e MINIO_ROOT_USER=minioadmin `
  -e MINIO_ROOT_PASSWORD=minioadmin `
  minio/minio server /data --console-address ":9001"
```

控制台 http://localhost:9001 ，创建 bucket `demo-files`（或让程序自动创建）。

## 运行

```powershell
uvicorn app.main:app --reload --port 8000
```

打开 http://localhost:8000/docs 查看 Swagger。

## 接口

### 1. 多文件上传

`POST /files/upload`  （multipart/form-data, 字段名 `files`，可多选）

返回：
```json
[
  {
    "id": 1,
    "original_name": "report.pdf",
    "storage_name": "9e1a...c2.pdf",
    "size": 12345,
    "content_type": "application/pdf",
    "created_at": "2026-05-12T10:00:00"
  }
]
```

### 2. 单文件下载

`GET /files/{file_id}/download` → 流式返回，文件名为 `original_name`。

### 3. 查询列表 / 详情

- `GET /files/` 列出所有
- `GET /files/{file_id}` 查看元数据

## 设计要点

- **S3 存储名唯一**：使用 `uuid4().hex + 原扩展名` 作为 object key，杜绝同名覆盖。
- **原名保留**：存入 `file_records.original_name`，下载时通过 `Content-Disposition` 回填。
- **大文件友好**：上传使用 `upload_fileobj` 流式；下载使用 `StreamingResponse`。
- **可替换存储后端**：`s3_client.py` 仅依赖 boto3 标准接口，AWS S3 / MinIO / 阿里云 OSS（兼容模式）均可。
