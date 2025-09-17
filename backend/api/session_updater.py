from backend.models.file import AccessFile
from fastapi import APIRouter, HTTPException
from backend.services.file_service import generate_and_save_cookies

router = APIRouter(prefix="/cookie", tags=["Cookie Updater"])

@router.post("/files/{file_id}/refresh_cookies")
async def refresh_cookies(file_id: int):
    file = await AccessFile.get_or_none(id=file_id)
    if not file:
        raise HTTPException(404, "Файл не найден")

    file = await generate_and_save_cookies(file)
    return {"status": "ok", "last_updated": file.last_updated}
