from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_name: str
    storage_name: str
    bucket: str
    content_type: str | None
    size: int
    created_at: datetime
