from backend.models.file import AccessFile
from tortoise.exceptions import DoesNotExist

class FileService:
    @staticmethod
    async def get_file(file_id: int) -> dict:
        file = await AccessFile.get_or_none(id=file_id)
        if not file:
            raise DoesNotExist(f"Файл {file_id} не найден")

        return {
            "id": file.id,
            "path": file.path,
            "login": file.login,
            "last_updated": file.last_updated,
            "locked_until": file.locked_until,
        }
