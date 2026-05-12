import os
import uuid
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import s3_client
from ..config import settings
from ..database import get_db
from ..models import FileRecord
from ..schemas import FileRecordOut

router = APIRouter(prefix="/files", tags=["files"])


def _build_storage_name(original_name: str) -> str:
    ext = os.path.splitext(original_name)[1]
    return f"{uuid.uuid4().hex}{ext}"


@router.post("/upload", response_model=list[FileRecordOut])
async def upload_files(
    files: list[UploadFile] = File(..., description="支持多文件"),
    db: Session = Depends(get_db),
):
    if not files:
        raise HTTPException(status_code=400, detail="未上传任何文件")

    records: list[FileRecord] = []
    for f in files:
        storage_name = _build_storage_name(f.filename or "unnamed")

        # 上传到 S3（流式）
        s3_client.upload_fileobj(f.file, storage_name, f.content_type)

        # 计算大小：seek 到末尾
        try:
            f.file.seek(0, os.SEEK_END)
            size = f.file.tell()
        except Exception:
            size = 0

        record = FileRecord(
            original_name=f.filename or storage_name,
            storage_name=storage_name,
            bucket=settings.s3_bucket,
            content_type=f.content_type,
            size=size,
        )
        db.add(record)
        records.append(record)

    db.commit()
    for r in records:
        db.refresh(r)
    return records


@router.get("/", response_model=list[FileRecordOut])
def list_files(db: Session = Depends(get_db)):
    return db.query(FileRecord).order_by(FileRecord.id.desc()).all()


@router.get("/{file_id}", response_model=FileRecordOut)
def get_file(file_id: int, db: Session = Depends(get_db)):
    record = db.get(FileRecord, file_id)
    if not record:
        raise HTTPException(status_code=404, detail="文件不存在")
    return record


@router.get("/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db)):
    record = db.get(FileRecord, file_id)
    if not record:
        raise HTTPException(status_code=404, detail="文件不存在")

    body, content_type, content_length = s3_client.get_object_stream(record.storage_name)

    def iterator(chunk_size: int = 64 * 1024):
        try:
            while True:
                chunk = body.read(chunk_size)
                if not chunk:
                    break
                yield chunk
        finally:
            body.close()

    filename_encoded = quote(record.original_name)
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{filename_encoded}",
    }
    if content_length:
        headers["Content-Length"] = str(content_length)

    return StreamingResponse(
        iterator(),
        media_type=content_type or record.content_type or "application/octet-stream",
        headers=headers,
    )
