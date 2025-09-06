from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class KnowledgeBaseBase(BaseModel):
    title: str
    file_path: str
    file_type_id: int
    content: Optional[str]
    uploaded_by_id: int


class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass


class KnowledgeBaseOut(KnowledgeBaseBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
