from tortoise import fields
from tortoise.models import Model

class KnowledgeBase(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(255)

    file_path = fields.CharField(255)
    file_type_id = fields.IntField()  # FK -> file_types
    content = fields.TextField(null=True)

    uploaded_by = fields.ForeignKeyField("models.User", related_name="kb_files")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "knowledge_base"
